# PHASE 1 — FUNCTIONAL REQUIREMENTS

## 1. Authentication & Account Management

**FR-AUTH-001 — Registration**
The system shall allow users to register according to their permitted role.

**FR-AUTH-002 — Authentication**
The system shall allow users to securely log in and log out.

**FR-AUTH-003 — Role Selection**
The system shall identify the user's role and provide the appropriate interface and permissions.

**FR-AUTH-004 — Profile Management**
Users shall be able to view and update their personal information.

**FR-AUTH-005 — Role-Based Authorization**
The system shall restrict functionality and data according to the user's role and permissions.

**FR-AUTH-006 — Account Recovery**
The system shall provide secure account recovery mechanisms.

**FR-AUTH-007 — Session Management**
The system shall securely manage authenticated sessions.

**FR-AUTH-008 — Audit Logging**
The system shall maintain logs for important security and administrative actions.

---

## 2. Student Requirements

### 2.1 Student Profile

**FR-STU-001**
Students shall create and maintain their professional profiles.

**FR-STU-002**
Students shall provide academic information.

**FR-STU-003**
Students shall add technical skills.

**FR-STU-004**
Students shall add soft skills.

**FR-STU-005**
Students shall add projects.

**FR-STU-006**
Students shall add certifications.

**FR-STU-007**
Students shall add achievements.

**FR-STU-008**
Students shall upload and maintain resumes.

**FR-STU-009**
Students shall maintain a digital portfolio.

**FR-STU-010**
Students shall specify their career interests.

**FR-STU-011**
Students shall specify preferred job roles and domains.

---

## 3. Skill Assessment

*This is one of the core modules of SkillBridge AI.*

**FR-SKL-001**
The system shall provide technical skill assessments.

**FR-SKL-002**
The system shall provide soft-skill assessments.

**FR-SKL-003**
The system shall provide aptitude assessments.

**FR-SKL-004**
The system shall support role-specific assessments.

**FR-SKL-005**
The system shall record assessment attempts.

**FR-SKL-006**
The system shall calculate assessment scores.

**FR-SKL-007**
The system shall map assessment results to corresponding skills.

**FR-SKL-008**
The system shall generate a skill profile from assessment results.

**FR-SKL-009**
The system shall track skill performance over time.

**FR-SKL-010**
The system shall allow students to retake eligible assessments.

**FR-SKL-011**
The system shall provide feedback after assessments.

---

## 4. Skill Profiling

*The assessment tells us what the student knows. The skill profile maintains the student's overall skill state.*

**FR-PROF-001**
The system shall maintain a structured skill profile for each student.

**FR-PROF-002**
The system shall record proficiency levels for individual skills.

**FR-PROF-003**
The system shall combine relevant evidence such as assessments, projects, certifications and experience when constructing the skill profile.

**FR-PROF-004**
The system shall allow skill proficiency to be updated when new evidence becomes available.

**FR-PROF-005**
The system shall display the student's current skill profile.

**FR-PROF-006**
The system shall show skill development history.

---

## 5. Skill Gap Analysis

*This is where we connect student capability → industry requirements.*

**FR-GAP-001**
The system shall maintain skill requirements for career roles.

**FR-GAP-002**
The system shall maintain skill requirements specified by industries.

**FR-GAP-003**
The system shall compare student skills with target-role requirements.

**FR-GAP-004**
The system shall identify missing skills.

**FR-GAP-005**
The system shall identify insufficiently developed skills.

**FR-GAP-006**
The system shall prioritize skill gaps.

**FR-GAP-007**
The system shall explain identified skill gaps.

**FR-GAP-008**
The system shall provide recommendations for reducing identified skill gaps.

**Example:**

```text
Target Role: Full-Stack Developer

Student Skill             Required Level
JavaScript        ████████  ✓
React             ██████    ✓
Node.js           ███       ⚠
SQL               ██        ⚠
Docker            █         ✗

Priority Skill Gaps:
1. Docker
2. SQL
3. Node.js

```

---

## 6. Career Intelligence

**FR-CAR-001**
The system shall maintain career-role profiles.

**FR-CAR-002**
The system shall map skills to career roles.

**FR-CAR-003**
The system shall recommend career roles based on student profiles.

**FR-CAR-004**
The system shall calculate career-role compatibility.

**FR-CAR-005**
The system shall explain career recommendations.

**FR-CAR-006**
Students shall be able to select target career roles.

**FR-CAR-007**
The system shall generate personalized career development roadmaps.

---

## 7. Learning & Skill Development

**FR-LEARN-001**
The system shall maintain learning resources.

**FR-LEARN-002**
The system shall maintain training programs.

**FR-LEARN-003**
The system shall recommend learning resources based on identified skill gaps.

**FR-LEARN-004**
The system shall recommend relevant training programs.

**FR-LEARN-005**
Students shall be able to enroll in available programs.

**FR-LEARN-006**
The system shall track learning progress.

**FR-LEARN-007**
The system shall track completed courses and certifications.

**FR-LEARN-008**
The system shall track skill improvement after training.

**FR-LEARN-009**
Mentors and trainers shall be able to create or manage permitted training content.

---

## 8. Industry Skill Requirements

**FR-IND-SKL-001**
Industry users shall be able to specify required skills for opportunities.

**FR-IND-SKL-002**
Industry users shall be able to specify required proficiency levels.

**FR-IND-SKL-003**
The system shall map skills to job roles.

**FR-IND-SKL-004**
The system shall identify skill requirements across industries.

**FR-IND-SKL-005**
The system shall generate industry skill-demand analytics.

**FR-IND-SKL-006**
The system shall identify frequently requested skills.

**FR-IND-SKL-007**
The system shall support identification of emerging skill requirements when sufficient data is available.

---

## 9. Internship Management

**FR-INT-001**
Industry users shall be able to create internship opportunities according to their permissions.

**FR-INT-002**
Industry users shall specify internship eligibility requirements.

**FR-INT-003**
Industry users shall specify required skills.

**FR-INT-004**
Students shall be able to search internship opportunities.

**FR-INT-005**
The system shall recommend relevant internships to students.

**FR-INT-006**
The system shall calculate student-internship compatibility.

**FR-INT-007**
Students shall be able to apply for internships.

**FR-INT-008**
Students shall be able to track applications.

**FR-INT-009**
Industry users shall be able to review applications.

**FR-INT-010**
Authorized industry users shall be able to shortlist candidates.

**FR-INT-011**
Mentors shall be able to monitor assigned interns.

**FR-INT-012**
Mentors shall be able to provide internship feedback.

**FR-INT-013**
The system shall maintain internship completion records.

---

## 10. Job & Placement Management

**FR-JOB-001**
Industry users shall be able to create job opportunities according to their permissions.

**FR-JOB-002**
Industry users shall define eligibility criteria.

**FR-JOB-003**
Industry users shall define required skills.

**FR-JOB-004**
Students shall be able to search job opportunities.

**FR-JOB-005**
The system shall recommend relevant jobs.

**FR-JOB-006**
The system shall calculate student-job compatibility.

**FR-JOB-007**
The system shall perform eligibility checking.

**FR-JOB-008**
Students shall be able to apply for jobs.

**FR-JOB-009**
Students shall be able to track applications.

**FR-JOB-010**
Industry users shall be able to review applications.

**FR-JOB-011**
Authorized industry users shall be able to shortlist candidates.

**FR-JOB-012**
The system shall track recruitment stages.

```text
Applied
   ↓
Screening
   ↓
Shortlisted
   ↓
Assessment
   ↓
Interview
   ↓
Selected
   ↓
Joined

```

---

## 11. Resume Intelligence

**FR-RES-001**
Students shall be able to upload resumes.

**FR-RES-002**
The system shall extract relevant information from resumes.

**FR-RES-003**
The system shall identify skills from resumes.

**FR-RES-004**
The system shall identify missing or potentially weak resume sections.

**FR-RES-005**
The system shall compare resumes with job requirements.

**FR-RES-006**
The system shall provide resume improvement recommendations.

**FR-RES-007**
Students shall be able to generate or update resumes using verified profile information.

---

## 12. Interview & Placement Preparation

**FR-PREP-001**
The system shall provide aptitude practice.

**FR-PREP-002**
The system shall provide technical assessments.

**FR-PREP-003**
The system shall provide role-specific interview preparation.

**FR-PREP-004**
The system shall provide interview question practice.

**FR-PREP-005**
The system shall provide mock interviews.

**FR-PREP-006**
The system shall provide feedback on mock interviews.

**FR-PREP-007**
The system shall identify areas requiring improvement.

**FR-PREP-008**
The system shall provide personalized preparation recommendations.

**FR-PREP-009**
The system shall track placement-preparation progress.

---

## 13. Employability / Placement Readiness

**FR-READY-001**
The system shall calculate a placement-readiness score.

**FR-READY-002**
The system shall consider relevant factors such as skills, assessments, projects, resume quality and preparation progress.

**FR-READY-003**
The system shall explain the factors contributing to the readiness score.

**FR-READY-004**
The system shall identify areas preventing the student from being placement-ready.

**FR-READY-005**
The system shall recommend actions to improve readiness.

---

## 14. Institution Requirements

*There are now two institution roles, so we'll explicitly separate their permissions.*

### Institution Normal User

**FR-INS-USER-001**
Institution users shall be able to view permitted student information.

**FR-INS-USER-002**
Institution users shall be able to participate in industry collaboration activities.

**FR-INS-USER-003**
Institution users shall be able to manage activities assigned to them.

**FR-INS-USER-004**
Institution users shall be able to access permitted analytics.

**FR-INS-USER-005**
Institution users shall be able to participate in mentorship, training and industry programs.

### Institution Admin

**FR-INS-ADMIN-001**
Institution administrators shall manage institution users.

**FR-INS-ADMIN-002**
Institution administrators shall manage student records according to institutional permissions.

**FR-INS-ADMIN-003**
Institution administrators shall manage academic departments/programs.

**FR-INS-ADMIN-004**
Institution administrators shall monitor student skill development.

**FR-INS-ADMIN-005**
Institution administrators shall monitor skill gaps.

**FR-INS-ADMIN-006**
Institution administrators shall monitor internship participation.

**FR-INS-ADMIN-007**
Institution administrators shall monitor placement progress.

**FR-INS-ADMIN-008**
Institution administrators shall monitor training participation.

**FR-INS-ADMIN-009**
Institution administrators shall analyze training effectiveness.

**FR-INS-ADMIN-010**
Institution administrators shall view industry skill-demand trends.

**FR-INS-ADMIN-011**
Institution administrators shall generate institutional reports.

---

## 15. Industry Requirements

### Industry Normal User

**FR-IND-USER-001**
Industry users shall manage opportunities assigned to them.

**FR-IND-USER-002**
Industry users shall review permitted candidate applications.

**FR-IND-USER-003**
Industry users shall participate in recruitment activities.

**FR-IND-USER-004**
Industry users shall provide candidate feedback.

**FR-IND-USER-005**
Industry users shall participate in mentorship and training activities.

### Industry Admin

**FR-IND-ADMIN-001**
Industry administrators shall manage industry users.

**FR-IND-ADMIN-002**
Industry administrators shall manage the organization profile.

**FR-IND-ADMIN-003**
Industry administrators shall create and manage jobs.

**FR-IND-ADMIN-004**
Industry administrators shall create and manage internships.

**FR-IND-ADMIN-005**
Industry administrators shall define organizational skill requirements.

**FR-IND-ADMIN-006**
Industry administrators shall manage recruitment activities.

**FR-IND-ADMIN-007**
Industry administrators shall manage industry training programs.

**FR-IND-ADMIN-008**
Industry administrators shall manage mentorship opportunities.

**FR-IND-ADMIN-009**
Industry administrators shall view recruitment analytics.

---

## 16. Mentor / Trainer Requirements

**FR-MENTOR-001**
Mentors/trainers shall maintain professional profiles.

**FR-MENTOR-002**
Mentors/trainers shall create permitted training programs.

**FR-MENTOR-003**
Mentors/trainers shall conduct training sessions.

**FR-MENTOR-004**
Mentors/trainers shall manage assigned students.

**FR-MENTOR-005**
Mentors/trainers shall monitor student progress.

**FR-MENTOR-006**
Mentors/trainers shall provide feedback.

**FR-MENTOR-007**
Mentors/trainers shall conduct assessments where authorized.

**FR-MENTOR-008**
Mentors/trainers shall provide mentorship.

**FR-MENTOR-009**
Mentors/trainers shall participate in industry projects.

---

## 17. Employment Outcome Tracking

*This directly addresses SIH26135.*

**FR-OUT-001**
The system shall record student placement outcomes.

**FR-OUT-002**
The system shall record employment status.

**FR-OUT-003**
The system shall record joining status.

**FR-OUT-004**
The system shall track employment outcomes after placement.

**FR-OUT-005**
The system shall track relevant career progression information where available and authorized.

**FR-OUT-006**
The system shall analyze training-to-placement outcomes.

**FR-OUT-007**
The system shall analyze training-to-employment outcomes.

**FR-OUT-008**
The system shall provide institution-level employment outcome analytics.

**FR-OUT-009**
The system shall provide relevant industry-level outcome analytics.

**FR-OUT-010**
The system shall use verified outcome data to improve relevant platform recommendations where appropriate.
