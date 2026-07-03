-- ============================================
-- 羽鲸校友系统 - SQL Server 建表脚本
-- 数据库: SolarOrcaAlumni
-- ============================================

-- 1. Users 表
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name NVARCHAR(200) NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    role VARCHAR(20) NULL,
    is_verified BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    salary INT NULL,
    location NVARCHAR(200) NULL,
    gender CHAR(1) NULL,
    graduation_year INT NULL
);

-- 2. Classes 表
CREATE TABLE Classes (
    class_id INT IDENTITY(1,1) PRIMARY KEY,
    faculty NVARCHAR(200) NOT NULL,
    major NVARCHAR(200) NOT NULL,
    class_number VARCHAR(20) NOT NULL,
    graduation_year INT NOT NULL
);

-- 3. UserClasses 表
CREATE TABLE UserClasses (
    user_id INT NOT NULL,
    class_id INT NOT NULL,
    PRIMARY KEY (user_id, class_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE CASCADE
);

-- 4. Degrees 表
CREATE TABLE Degrees (
    degree_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    degree_type VARCHAR(30) NULL,
    major NVARCHAR(200) NULL,
    institution NVARCHAR(400) NULL,
    start_year INT NULL,
    end_year INT NULL,
    minor NVARCHAR(200) NULL,
    certificate NVARCHAR(200) NULL,
    original_major NVARCHAR(200) NULL,
    transfer_year INT NULL,
    second_degree NVARCHAR(200) NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 5. WorkExperience 表
CREATE TABLE WorkExperience (
    work_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    job_title NVARCHAR(200) NOT NULL,
    employer NVARCHAR(200) NOT NULL,
    start_year INT NOT NULL,
    end_year INT NULL,
    is_current BIT DEFAULT 0,
    industry NVARCHAR(100) NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 6. ResearchPositions 表
CREATE TABLE ResearchPositions (
    position_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    position_type VARCHAR(50) NOT NULL,
    institution NVARCHAR(400) NOT NULL,
    department NVARCHAR(200) NULL,
    start_year INT NOT NULL,
    end_year INT NULL,
    is_current BIT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 7. Threads 表
CREATE TABLE Threads (
    thread_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    title NVARCHAR(400) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    is_pinned BIT DEFAULT 0,
    is_locked BIT DEFAULT 0,
    is_alumni_only BIT DEFAULT 0,
    view_count INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 8. Replies 表
CREATE TABLE Replies (
    reply_id INT IDENTITY(1,1) PRIMARY KEY,
    thread_id INT NOT NULL,
    user_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (thread_id) REFERENCES Threads(thread_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 9. Reports 表
CREATE TABLE Reports (
    report_id INT IDENTITY(1,1) PRIMARY KEY,
    reporter_user_id INT NOT NULL,
    thread_id INT NULL,
    reply_id INT NULL,
    reason NVARCHAR(200) NOT NULL,
    details NVARCHAR(1000) NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (reporter_user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (thread_id) REFERENCES Threads(thread_id) ON DELETE CASCADE,
    FOREIGN KEY (reply_id) REFERENCES Replies(reply_id) ON DELETE CASCADE,
    CHECK (thread_id IS NOT NULL OR reply_id IS NOT NULL)
);

-- 10. PasswordResetTokens 表
CREATE TABLE PasswordResetTokens (
    reset_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 11. UserNotifications 表
CREATE TABLE UserNotifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    title NVARCHAR(400) NOT NULL,
    message NVARCHAR(1000) NOT NULL,
    is_read BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 12. VerificationTokens 表
CREATE TABLE VerificationTokens (
    token_id INT IDENTITY(1,1) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE()
);

-- 13. Announcements 表
CREATE TABLE Announcements (
    announcement_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    expires_at DATETIME NULL
);