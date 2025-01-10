# Application-Management-System

The **Application Management System** is a Python-based project designed to streamline the process of managing job applications. This system allows administrators to submit, review, and make decisions on applications efficiently. It also provides features like searching, filtering, and generating detailed reports on applications.

---

## Features

### Core Features
1. **Submit New Application**:
   - Add a new application with details such as:
     - Applicant's name
     - Job ID
     - Resume link
     - Skills
     - Years of experience
   - Automatically assigns a unique application ID.
   - Adds the application to a review queue.

2. **Process Next Application**:
   - Processes the next application in the review queue.
   - Updates the application's status to **under_review**.
   - Allows the reviewer to record a decision as **shortlisted** or **rejected**.

3. **View Application Queue**:
   - Displays the list of applications currently in the review queue.

4. **Search Applications**:
   - Search applications based on:
     - Applicant's name
     - Job ID
     - Application status (e.g., submitted, under_review, shortlisted, rejected)

5. **Filter Applications**:
   - Filter applications based on:
     - Minimum years of experience
     - Required skills

6. **Generate Reports**:
   - Provides a summary report of all applications, including:
     - Total applications
     - Applications grouped by job position
     - Count of applications by status (submitted, under_review, shortlisted, rejected)

---

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/deepeshyadav760/application-management-system.git
   cd application-management-system


