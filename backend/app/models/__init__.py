from app.models.user import User
from app.models.student import *
from app.models.skill import Skill
from app.models.career import CareerRole
from app.models.document import StudentDocument
from app.models.audit import AuditLog
from app.models.intelligence import EmploymentOutcome, AIExecution, Recommendation
from app.models.learning import LearningResource, StudentLearningPlan, LearningPlanItem, LearningCertification, LearningOutcome
from app.models.opportunities import InternshipPosting, AcademicianOpportunity, InternshipApplication, InternshipProgress, InternshipMentorFeedback
from app.models.assessment import Assessment, Question, CodingChallenge, AssessmentAttempt, AssessmentResponse
from app.models.interview import InterviewSession, InterviewTurn, InterviewEvaluation
from app.models.institution import InstitutionDepartment, StudentPlacementReadiness
from app.models.industry import IndustryOpportunity, IndustryFeedback
from app.models.organization import Organization, OrganizationMembership
from app.models.mentorship import MentorAssignment
from app.models.notification import Notification
