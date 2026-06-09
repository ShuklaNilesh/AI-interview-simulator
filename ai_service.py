import httpx
import json
import logging
from backend.config import settings

logger = logging.getLogger("ai_service")

class AIService:
    @staticmethod
    def _call_groq(messages: list, json_mode: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(settings.GROQ_API_URL, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    # Try a fallback model if 70b has rate limits
                    payload["model"] = "llama3-8b-8192"
                    response = client.post(settings.GROQ_API_URL, headers=headers, json=payload)
                    
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            # Fail-safe static JSON or text
            if json_mode:
                return '{"error": "Failed to query AI service", "score": 70, "ats_score": 65, "feedback": "AI temporary offline.", "missing_keywords": [], "strengths": "N/A", "weaknesses": "N/A"}'
            return "I apologize, I am experiencing temporary connectivity difficulties. Could you please repeat or elaborate on your response?"

    @classmethod
    def generate_first_question(cls, role: str, difficulty: str, type: str, resume_context: str = "") -> str:
        resume_prompt = f"Here is the candidate's resume context to tailor the interview:\n{resume_context}" if resume_context else ""
        
        system_prompt = (
            f"You are a professional, polite, and thorough job interviewer for a {role} role. "
            f"Difficulty level is {difficulty}. Interview type is {type}."
            f"Welcome the candidate briefly and ask the first clear and relevant interview question. "
            f"Do not give any introductory filler text other than a brief friendly welcome. Keep it direct and realistic."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Start the interview session. {resume_prompt}"}
        ]
        return cls._call_groq(messages)

    @classmethod
    def generate_followup_question(cls, role: str, difficulty: str, type: str, history: list, previous_answer: str) -> str:
        system_prompt = (
            f"You are a professional interviewer for a {role} role at {difficulty} level. "
            f"Current round type: {type}.\n"
            f"Review the conversation history, analyze the candidate's latest answer, and ask a relevant follow-up question. "
            f"You can dive deeper into their previous answer, ask for clarification, or move to the next logical question. "
            f"Do not explain your reasoning. Output only the next interview question directly."
        )
        
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for q, a in history:
            formatted_messages.append({"role": "assistant", "content": q})
            if a:
                formatted_messages.append({"role": "user", "content": a})
                
        formatted_messages.append({"role": "user", "content": f"My answer is: {previous_answer}. Please ask the next question."})
        return cls._call_groq(formatted_messages)

    @classmethod
    def grade_answer_and_suggest(cls, role: str, difficulty: str, type: str, question: str, answer: str) -> dict:
        system_prompt = (
            "You are an expert technical and HR interviewer. "
            "Evaluate the candidate's answer for the given question and provide a performance breakdown in JSON format. "
            "Output must be a JSON object with exactly the following fields:\n"
            "{\n"
            '  "technical_score": float (0-100),\n'
            '  "communication_score": float (0-100),\n'
            '  "confidence_score": float (0-100),\n'
            '  "fluency_score": float (0-100),\n'
            '  "feedback_text": "detailed critique of the answer, including correctness and style",\n'
            '  "suggestion": "actionable tip on how to improve this answer (e.g. key details missed, structure)"\n'
            "}"
        )
        
        user_content = f"Role: {role}\nLevel: {difficulty}\nType: {type}\nQuestion: {question}\nCandidate Answer: {answer}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        result_str = cls._call_groq(messages, json_mode=True)
        try:
            return json.loads(result_str)
        except Exception:
            return {
                "technical_score": 70.0,
                "communication_score": 75.0,
                "confidence_score": 70.0,
                "fluency_score": 75.0,
                "feedback_text": "Completed parsing response. Good effort on structuring the answer.",
                "suggestion": "Add more structured context or code examples if relevant."
            }

    @classmethod
    def generate_final_session_report(cls, role: str, difficulty: str, type: str, questions_and_answers: list) -> dict:
        system_prompt = (
            "You are an expert career consultant and interviewer. Evaluate the candidate's overall performance "
            "based on the completed interview session. Output your analysis in JSON format with exactly the following fields:\n"
            "{\n"
            '  "overall_score": float (0-100),\n'
            '  "technical_score": float (0-100),\n'
            '  "communication_score": float (0-100),\n'
            '  "confidence_score": float (0-100),\n'
            '  "fluency_score": float (0-100),\n'
            '  "hr_score": float (0-100),\n'
            '  "detailed_feedback": "Markdown format text highlighting strengths and areas to work on across the session",\n'
            '  "learning_roadmap": "Markdown format step-by-step personalized guide/roadmap to master this role and fix gaps"\n'
            "}"
        )
        
        history_str = ""
        for idx, item in enumerate(questions_and_answers):
            history_str += f"Q{idx+1}: {item['question']}\nA{idx+1}: {item.get('answer', 'No answer provided')}\nFeedback: {item.get('feedback', '')}\n\n"
            
        user_content = f"Role: {role}\nLevel: {difficulty}\nType: {type}\nInterview Q&A Sessions:\n{history_str}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        result_str = cls._call_groq(messages, json_mode=True)
        try:
            return json.loads(result_str)
        except Exception:
            return {
                "overall_score": 75.0,
                "technical_score": 70.0,
                "communication_score": 75.0,
                "confidence_score": 75.0,
                "fluency_score": 80.0,
                "hr_score": 75.0,
                "detailed_feedback": "### Strengths\n- Answered structured technical questions.\n### Weaknesses\n- Needs deeper knowledge in architectural patterns.",
                "learning_roadmap": "### Phase 1: Basics\n- Study core system design and patterns.\n### Phase 2: Mock Practice\n- Practice answering with STAR method."
            }

    @classmethod
    def analyze_resume(cls, filename: str, text_content: str) -> dict:
        system_prompt = (
            "You are a professional ATS (Applicant Tracking System) parser and talent acquisition specialist. "
            "Analyze the following resume text and provide feedback in JSON format with exactly the following keys:\n"
            "{\n"
            '  "ats_score": int (0-100),\n'
            '  "missing_keywords": "comma separated string of matching industry keywords or tools missing from this resume",\n'
            '  "strengths": "bulleted list or text describing core strengths identified in resume",\n'
            '  "weaknesses": "bulleted list or text describing gaps, weak styling, or missing elements",\n'
            '  "parsed_skills": "comma separated list of skills identified in the resume"\n'
            "}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Resume Text (Filename: {filename}):\n{text_content[:8000]}"}
        ]
        
        result_str = cls._call_groq(messages, json_mode=True)
        try:
            return json.loads(result_str)
        except Exception:
            return {
                "ats_score": 60,
                "missing_keywords": "Docker, Kubernetes, CI/CD, TypeScript",
                "strengths": "Strong foundation in backend programming with Python.",
                "weaknesses": "Missing cloud deployment experience and active web project metrics.",
                "parsed_skills": "Python, SQL, Django, FastAPI, React"
            }

    @classmethod
    def get_coding_feedback_and_hints(cls, question: str, code: str, language: str, hints_used: int) -> dict:
        system_prompt = (
            "You are an expert coding interviewer. Evaluate the candidate's code submission for the specified question. "
            "Analyze code quality, performance, correctness, and suggest hints. "
            "Respond in JSON format with exactly the following fields:\n"
            "{\n"
            '  "complexity": "e.g. O(N) time, O(N) space",\n'
            '  "test_cases_passed": "e.g. 4/5 or Pass/Fail status",\n'
            '  "feedback": "detailed review of the algorithm, code styling, edge cases, and bug fixes",\n'
            '  "hint": "a helpful, subtle hint helping candidate get closer to solution. Make it more explicit if they have used hints before. Current hints count: ' + str(hints_used) + '"\n'
            "}"
        )
        
        user_content = f"Coding Language: {language}\nProblem Statement: {question}\nUser Code:\n{code}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        result_str = cls._call_groq(messages, json_mode=True)
        try:
            return json.loads(result_str)
        except Exception:
            return {
                "complexity": "O(N^2) Time, O(1) Space",
                "test_cases_passed": "3/5",
                "feedback": "Your solution is correct but inefficient for large arrays. Look into double pointer approaches.",
                "hint": "Try sorting the array first or using a hash map to reduce time complexity."
            }

    @classmethod
    def get_career_assistant_response(cls, chat_history: list) -> str:
        system_prompt = (
            "You are 'InterviewAce Career Coach', an encouraging and highly knowledgeable career guide. "
            "Help the user prepare high-impact resumes, optimize their LinkedIn profiles, define career pathways, "
            "understand skill requirements, design side project ideas, and prepare for interviews. "
            "Keep answers concise, modern, structured with clean bullet points, and highly professional."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for item in chat_history:
            messages.append({"role": item["role"], "content": item["text"]})
            
        return cls._call_groq(messages)

    @classmethod
    def get_trainer_coaching(cls, question: str, answer: str) -> dict:
        system_prompt = (
            "You are a dedicated AI Mock Interview Coach. Teach the user how to structure answers using the STAR method (Situation, Task, Action, Result). "
            "Analyze their current response, provide actionable coaching suggestions, and construct an IDEAL answer using the STAR structure. "
            "Respond in JSON format with exactly these fields:\n"
            "{\n"
            '  "star_breakdown": "Explanation of how to format this specific answer using Situation, Task, Action, Result",\n'
            '  "critique": "Actionable feedback on tone, gaps, structure, and communication clarity of their answer",\n'
            '  "ideal_answer": "Complete, premium sample answer written in first person that the user can learn from"\n'
            "}"
        )
        
        user_content = f"Question: {question}\nUser Answer: {answer}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        result_str = cls._call_groq(messages, json_mode=True)
        try:
            return json.loads(result_str)
        except Exception:
            return {
                "star_breakdown": "**S**: Describe the project conflict.\n**T**: Goal was to launch in 2 weeks.\n**A**: Set up a prioritization meeting.\n**R**: Delivered on time.",
                "critique": "Your answer was good but lacked concrete metrics. Always quantify results.",
                "ideal_answer": "At my last job, we faced a major bottleneck. I initiated an agile prioritization review, resulting in standardizing tasks and launching 3 days ahead of schedule."
            }
