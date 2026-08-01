-- SQL Initialization Script
-- Run as root to set up database and user

-- Create database
CREATE DATABASE IF NOT EXISTS company_db;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'aparichit'@'localhost' IDENTIFIED BY 'letmelogin';
GRANT ALL PRIVILEGES ON company_db.* TO 'aparichit'@'localhost';
FLUSH PRIVILEGES;

USE company_db;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS projects;

-- Create employees table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    department VARCHAR(100),
    salary DECIMAL(10,2),
    phone VARCHAR(20),
    credit_card VARCHAR(20)
);

-- Create projects table
CREATE TABLE projects (
    project_id INT PRIMARY KEY,
    project_name VARCHAR(100),
    budget DECIMAL(12,2),
    status VARCHAR(50)
);

-- Create performance reviews table
CREATE TABLE performance_reviews (
    review_id INT PRIMARY KEY,
    employee_id INT,
    rating INT,
    comments TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);
