import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    INDUSTRY = "industry"
    INSTITUTION = "institution"
    ACADEMICIAN = "academician"
    ADMIN = "admin"

class AssessmentType(str, enum.Enum):
    APTITUDE = "aptitude"
    TECHNICAL_MCQ = "technical_mcq"
    CODING = "coding"
    DOMAIN_SPECIFIC = "domain_specific"

class QuestionType(str, enum.Enum):
    MCQ_SINGLE = "mcq_single"
    MCQ_MULTIPLE = "mcq_multiple"
    CODING = "coding"
    SUBJECTIVE = "subjective"

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InterviewType(str, enum.Enum):
    TECHNICAL = "technical"
    HR_BEHAVIORAL = "hr_behavioral"
    COMPANY_SPECIFIC = "company_specific"
    SYSTEM_DESIGN = "system_design"

class SessionStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EVALUATED = "evaluated"
    ABANDONED = "abandoned"
