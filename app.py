#!/usr/bin/env python3
# Garena Account Manager - Mobile Optimized Pro Edition
# Features: Sticky Back Button, Step Guide Box, Mobile-First Design

from flask import Flask, render_template_string, request, jsonify, session, send_file
import requests
import json
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
APP_ID = "100067"
BASE_URL = "https://100067.connect.garena.com/game/account_security"
CANCEL_URL = "https://100067.connect.gopapi.io/game/account_security"
BIND_INFO_URL = "https://bind-info-senku.vercel.app/bind_info"
EAT_CONVERT_URL = "https://eat-to-access-beta.vercel.app/eat_to_access"

STANDARD_HEADERS = {
    'User-Agent': 'GarenaMSDK/4.0.39(GFY-LX3 ;Android 13;en;HK;)',
    'Connection': 'Keep-Alive',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'datadome=XjUykstNTPfQcRhQ6hLhjpqgsuvxVM8gvP59Zsfahr4DRCkZSSQzvYZUmslLlknS9AS3aPFG3S3Z_~SMn7ulGH9cawYoziogCS5sTm6hoW35ctShDcf7U90fYTkaSEaA'
}

class GarenaAPI:
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update(STANDARD_HEADERS)
    
    def is_success(self, result):
        return result.get('result') == 0 or result.get('error') == 0
    
    def send_otp(self, email, locale='en_HK', region='HK'):
        url = f"{BASE_URL}/bind:send_otp"
        data = {'app_id': APP_ID, 'access_token': self.access_token, 'email': email, 'locale': locale, 'region': region}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            return (True, result) if (response.status_code == 200 and self.is_success(result)) else (False, result.get('message') or result.get('error_msg') or 'Unknown error')
        except Exception as e:
            return False, str(e)
    
    def verify_otp(self, otp, email):
        url = f"{BASE_URL}/bind:verify_otp"
        data = {'app_id': APP_ID, 'access_token': self.access_token, 'otp': otp, 'email': email}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            if response.status_code == 200 and self.is_success(result):
                token = result.get('data', {}).get('verifier_token') or result.get('verifier_token') or result.get('token') or result.get('data', {}).get('token')
                return (True, token) if token else (False, "No verifier token")
            return False, result.get('message') or result.get('error_msg') or 'Verification failed'
        except Exception as e:
            return False, str(e)
    
    def create_bind_request(self, verifier_token, email, secondary_password=None):
        if not secondary_password:
            secondary_password = "3A43F5AE7A96BAE91481F6225AC98A378CA08EBE92DAC680AAABE41E82102179"
        url = f"{BASE_URL}/bind:create_bind_request"
        data = {'app_id': APP_ID, 'access_token': self.access_token, 'verifier_token': verifier_token, 'secondary_password': secondary_password, 'email': email}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            return (True, result) if (response.status_code == 200 and self.is_success(result)) else (False, result.get('message') or 'Bind failed')
        except Exception as e:
            return False, str(e)
    
    def verify_identity(self, email, otp):
        url = f"{BASE_URL}/bind:verify_identity"
        data = {'app_id': APP_ID, 'access_token': self.access_token, 'otp': otp, 'email': email}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            if response.status_code == 200 and self.is_success(result):
                identity_token = result.get('identity_token')
                return (True, identity_token) if identity_token else (False, "No identity token")
            return False, result.get('message') or 'Identity verification failed'
        except Exception as e:
            return False, str(e)
    
    def create_rebind_request(self, identity_token, new_email, verifier_token):
        url = f"{BASE_URL}/bind:create_rebind_request"
        data = {'identity_token': identity_token, 'email': new_email, 'app_id': APP_ID, 'verifier_token': verifier_token, 'access_token': self.access_token}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            return (True, result) if (response.status_code == 200 and self.is_success(result)) else (False, result.get('message') or 'Rebind failed')
        except Exception as e:
            return False, str(e)
    
    def create_unbind_request(self, identity_token):
        url = f"{BASE_URL}/bind:create_unbind_request"
        data = {'app_id': APP_ID, 'access_token': self.access_token, 'identity_token': identity_token}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            return (True, result) if (response.status_code == 200 and self.is_success(result)) else (False, result.get('message') or 'Unbind failed')
        except Exception as e:
            return False, str(e)
    
    def cancel_request(self):
        url = f"{CANCEL_URL}/bind:cancel_request"
        data = {'app_id': APP_ID, 'access_token': self.access_token}
        try:
            response = self.session.post(url, data=data, timeout=10)
            result = response.json()
            return (True, result) if (response.status_code == 200 and self.is_success(result)) else (False, result.get('message') or 'Cancel failed')
        except Exception as e:
            return False, str(e)

def get_bind_info(access_token):
    try:
        url = f"{BIND_INFO_URL}?access_token={access_token}"
        response = requests.get(url, timeout=10)
        return (True, response.json()) if response.status_code == 200 else (False, f"HTTP {response.status_code}")
    except Exception as e:
        return False, str(e)

def convert_eat_to_access(eat_token):
    try:
        url = f"{EAT_CONVERT_URL}?eat_token={eat_token}"
        response = requests.get(url, timeout=10)
        return (True, response.json()) if response.status_code == 200 else (False, f"HTTP {response.status_code}")
    except Exception as e:
        return False, str(e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Garena Manager Pro | SenkuCodex</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --bg-input: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border: #475569;
            --header-height: 60px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            padding-bottom: 80px;
            line-height: 1.6;
        }

        /* Sticky Header */
        .sticky-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1rem;
        }

        .sticky-header .logo {
            font-size: 1.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #ec4899);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .back-btn-top {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
        }

        .back-btn-top:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(-3px);
        }

        .back-btn-top.hidden {
            display: none;
        }

        /* Main Content Padding for Fixed Header */
        .main-content {
            margin-top: var(--header-height);
            padding: 1rem;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }

        /* Dashboard Grid */
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
            padding: 0.5rem 0;
        }

        .card {
            background: var(--bg-card);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transform: scaleX(0);
            transition: transform 0.3s;
        }

        .card:hover::before,
        .card:active::before {
            transform: scaleX(1);
        }

        .card:active {
            transform: scale(0.98);
        }

        .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: white;
        }

        .card h3 {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .card p {
            font-size: 0.85rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .card-badge {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(99, 102, 241, 0.2);
            color: var(--primary);
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 700;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        /* Form Container */
        .form-wrapper {
            display: none;
            animation: fadeIn 0.4s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .form-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        @media (min-width: 968px) {
            .form-layout {
                grid-template-columns: 1fr 320px;
                align-items: start;
            }
        }

        /* Guide Box - Step by Step */
        .guide-box {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1));
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 1.5rem;
            position: sticky;
            top: calc(var(--header-height) + 1rem);
        }

        .guide-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--primary);
        }

        .guide-step {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            opacity: 0.5;
            transition: all 0.3s;
        }

        .guide-step.active {
            opacity: 1;
        }

        .guide-step.completed {
            opacity: 0.7;
        }

        .guide-step.completed .step-number {
            background: var(--success);
            color: white;
        }

        .step-number {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: var(--bg-input);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 700;
            flex-shrink: 0;
            border: 2px solid transparent;
            transition: all 0.3s;
        }

        .guide-step.active .step-number {
            background: var(--primary);
            color: white;
            border-color: rgba(255, 255, 255, 0.5);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
        }

        .step-content h4 {
            font-size: 0.9rem;
            margin-bottom: 0.2rem;
            font-weight: 600;
        }

        .step-content p {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        /* Form Card */
        .form-card {
            background: var(--bg-card);
            border-radius: 24px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .form-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .form-title i {
            color: var(--primary);
        }

        .form-group {
            margin-bottom: 1.25rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .input-wrapper {
            position: relative;
        }

        .input-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 1rem;
        }

        input {
            width: 100%;
            padding: 0.875rem 1rem 0.875rem 2.75rem;
            background: var(--bg-input);
            border: 2px solid var(--border);
            border-radius: 14px;
            color: var(--text-primary);
            font-size: 1rem;
            font-family: 'JetBrains Mono', monospace;
            transition: all 0.3s;
        }

        input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        input::placeholder {
            color: var(--text-secondary);
            opacity: 0.6;
        }

        /* Buttons */
        .btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border: none;
            border-radius: 14px;
            color: white;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            touch-action: manipulation;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .btn-secondary {
            background: var(--bg-input);
            border: 2px solid var(--border);
        }

        .btn-success {
            background: linear-gradient(135deg, var(--success), #059669);
        }

        .btn-sm {
            padding: 0.75rem;
            font-size: 0.9rem;
        }

        /* Step Content Animation */
        .step-content-form {
            display: none;
        }

        .step-content-form.active {
            display: block;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(10px); }
            to { opacity: 1; transform: translateX(0); }
        }

        /* Result Box */
        .result-box {
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 16px;
            display: none;
            border: 2px solid transparent;
        }

        .result-box.show {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        .result-box.success {
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .result-box.error {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
        }

        .result-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }

        .result-box.success .result-header { color: var(--success); }
        .result-box.error .result-header { color: var(--error); }

        .result-content {
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem;
            border-radius: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
        }

        /* Toast Notifications */
        .toast-container {
            position: fixed;
            top: calc(var(--header-height) + 0.5rem);
            left: 1rem;
            right: 1rem;
            z-index: 2000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            pointer-events: none;
        }

        .toast {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            animation: slideDown 0.3s ease;
            pointer-events: all;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .toast.success { border-color: var(--success); }
        .toast.error { border-color: var(--error); }

        .toast-icon { font-size: 1.25rem; }
        .toast.success .toast-icon { color: var(--success); }
        .toast.error .toast-icon { color: var(--error); }

        .toast-content { flex: 1; }
        .toast-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 0.1rem; }
        .toast-message { font-size: 0.8rem; color: var(--text-secondary); }

        /* Loading Spinner */
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* Mobile Optimizations */
        @media (max-width: 480px) {
            :root { --header-height: 56px; }
            
            .sticky-header .logo { font-size: 1rem; }
            .back-btn-top { padding: 0.4rem 0.8rem; font-size: 0.8rem; }
            
            .main-content { padding: 0.75rem; }
            
            .card { padding: 1.25rem; }
            .card h3 { font-size: 1rem; }
            .card p { font-size: 0.8rem; }
            
            .form-card { padding: 1.25rem; }
            .form-title { font-size: 1.1rem; }
            
            input { font-size: 16px; padding: 0.75rem 0.75rem 0.75rem 2.5rem; }
            .input-icon { left: 0.75rem; font-size: 0.9rem; }
            
            .guide-box { 
                position: relative; 
                top: 0; 
                order: -1;
                padding: 1rem;
            }
            
            .guide-step { gap: 0.75rem; margin-bottom: 0.75rem; }
            .step-number { width: 24px; height: 24px; font-size: 0.75rem; }
            .step-content h4 { font-size: 0.85rem; }
            .step-content p { font-size: 0.75rem; }
        }

        /* Scrollbar Styling */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }
    </style>
</head>
<body>
    <!-- Sticky Header with Back Button -->
    <header class="sticky-header">
        <div class="logo">
            <i class="fas fa-shield-alt"></i>
            <span>Garena Manager</span>
        </div>
        <button class="back-btn-top hidden" id="backBtn" onclick="goBack()">
            <i class="fas fa-arrow-left"></i>
            <span>Back</span>
        </button>
    </header>

    <!-- Toast Container -->
    <div class="toast-container" id="toastContainer"></div>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Dashboard Grid -->
        <div id="dashboard" class="dashboard">
            <div class="card" onclick="showForm('bind')">
                <div class="card-badge">3 Steps</div>
                <div class="card-icon"><i class="fas fa-envelope"></i></div>
                <h3>Bind Recovery Email</h3>
                <p>Add new recovery email to your Garena account</p>
            </div>

            <div class="card" onclick="showForm('change')">
                <div class="card-badge">5 Steps</div>
                <div class="card-icon"><i class="fas fa-exchange-alt"></i></div>
                <h3>Change Email</h3>
                <p>Update existing email to new one</p>
            </div>

            <div class="card" onclick="showForm('unbind')">
                <div class="card-badge">3 Steps</div>
                <div class="card-icon"><i class="fas fa-unlink"></i></div>
                <h3>Unbind Email</h3>
                <p>Remove linked email from account</p>
            </div>

            <div class="card" onclick="showForm('cancel')">
                <div class="card-badge">Quick</div>
                <div class="card-icon"><i class="fas fa-ban"></i></div>
                <h3>Cancel Request</h3>
                <p>Cancel pending bind/unbind request</p>
            </div>

            <div class="card" onclick="showForm('info')">
                <div class="card-badge">Instant</div>
                <div class="card-icon"><i class="fas fa-info-circle"></i></div>
                <h3>Bind Info</h3>
                <p>Check current binding status</p>
            </div>

            <div class="card" onclick="showForm('eat')">
                <div class="card-badge">Tool</div>
                <div class="card-icon"><i class="fas fa-key"></i></div>
                <h3>EAT Converter</h3>
                <p>Convert EAT to Access Token</p>
            </div>
        </div>

        <!-- Bind Form with Step Guide -->
        <div id="bindForm" class="form-wrapper">
            <div class="form-layout">
                <div class="form-card">
                    <h2 class="form-title"><i class="fas fa-envelope"></i> Bind Recovery Email</h2>
                    
                    <div id="bind-step1" class="step-content-form active">
                        <div class="form-group">
                            <label>Access Token</label>
                            <div class="input-wrapper">
                                <i class="fas fa-key input-icon"></i>
                                <input type="text" id="bind_token" placeholder="Paste access token here">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Email Address</label>
                            <div class="input-wrapper">
                                <i class="fas fa-envelope input-icon"></i>
                                <input type="email" id="bind_email" placeholder="Enter email to bind">
                            </div>
                        </div>
                        <button class="btn" onclick="bindStep1()">
                            <i class="fas fa-paper-plane"></i> Send OTP
                        </button>
                    </div>

                    <div id="bind-step2" class="step-content-form">
                        <div class="form-group">
                            <label>OTP Code</label>
                            <div class="input-wrapper">
                                <i class="fas fa-shield-alt input-icon"></i>
                                <input type="text" id="bind_otp" placeholder="Enter 6-digit code">
                            </div>
                        </div>
                        <button class="btn" onclick="bindStep2()">
                            <i class="fas fa-check"></i> Verify OTP
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="bindStep1()">
                            <i class="fas fa-redo"></i> Resend OTP
                        </button>
                    </div>

                    <div id="bind-step3" class="step-content-form">
                        <div class="form-group">
                            <label>Secondary Password (Optional)</label>
                            <div class="input-wrapper">
                                <i class="fas fa-lock input-icon"></i>
                                <input type="text" id="bind_secondary" placeholder="Leave blank for default">
                            </div>
                        </div>
                        <button class="btn btn-success" onclick="bindStep3()">
                            <i class="fas fa-lock"></i> Complete Binding
                        </button>
                    </div>

                    <div id="bind_result" class="result-box">
                        <div class="result-header"></div>
                        <div class="result-content"></div>
                    </div>
                </div>

                <!-- Step by Step Guide Box -->
                <div class="guide-box">
                    <div class="guide-title">
                        <i class="fas fa-list-ol"></i>
                        Step Guide
                    </div>
                    <div class="guide-step active" data-step="1">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h4>Send OTP</h4>
                            <p>Enter your access token and new email. Click Send OTP.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="2">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h4>Verify Code</h4>
                            <p>Check your email inbox and enter the 6-digit OTP code.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="3">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h4>Complete</h4>
                            <p>Click Complete Binding to finish. Optional: Add secondary password.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Change Form with Step Guide -->
        <div id="changeForm" class="form-wrapper">
            <div class="form-layout">
                <div class="form-card">
                    <h2 class="form-title"><i class="fas fa-exchange-alt"></i> Change Email</h2>
                    
                    <div id="change-step1" class="step-content-form active">
                        <div class="form-group">
                            <label>Access Token</label>
                            <div class="input-wrapper">
                                <i class="fas fa-key input-icon"></i>
                                <input type="text" id="change_token" placeholder="Paste access token">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Current Email (Old)</label>
                            <div class="input-wrapper">
                                <i class="fas fa-envelope input-icon"></i>
                                <input type="email" id="change_old_email" placeholder="Enter current email">
                            </div>
                        </div>
                        <button class="btn" onclick="changeStep1()">
                            <i class="fas fa-paper-plane"></i> Send OTP to Old
                        </button>
                    </div>

                    <div id="change-step2" class="step-content-form">
                        <div class="form-group">
                            <label>OTP from Old Email</label>
                            <div class="input-wrapper">
                                <i class="fas fa-shield-alt input-icon"></i>
                                <input type="text" id="change_otp_old" placeholder="Enter OTP">
                            </div>
                        </div>
                        <button class="btn" onclick="changeStep2()">
                            <i class="fas fa-check"></i> Verify Identity
                        </button>
                    </div>

                    <div id="change-step3" class="step-content-form">
                        <div class="form-group">
                            <label>New Email Address</label>
                            <div class="input-wrapper">
                                <i class="fas fa-envelope input-icon"></i>
                                <input type="email" id="change_new_email" placeholder="Enter new email">
                            </div>
                        </div>
                        <button class="btn" onclick="changeStep3()">
                            <i class="fas fa-paper-plane"></i> Send OTP to New
                        </button>
                    </div>

                    <div id="change-step4" class="step-content-form">
                        <div class="form-group">
                            <label>OTP from New Email</label>
                            <div class="input-wrapper">
                                <i class="fas fa-shield-alt input-icon"></i>
                                <input type="text" id="change_otp_new" placeholder="Enter OTP">
                            </div>
                        </div>
                        <button class="btn" onclick="changeStep4()">
                            <i class="fas fa-check"></i> Verify New Email
                        </button>
                    </div>

                    <div id="change-step5" class="step-content-form">
                        <button class="btn btn-success" onclick="changeStep5()">
                            <i class="fas fa-exchange-alt"></i> Confirm Change
                        </button>
                    </div>

                    <div id="change_result" class="result-box">
                        <div class="result-header"></div>
                        <div class="result-content"></div>
                    </div>
                </div>

                <div class="guide-box">
                    <div class="guide-title"><i class="fas fa-list-ol"></i> Step Guide</div>
                    <div class="guide-step active" data-step="1">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h4>Verify Old Email</h4>
                            <p>Send OTP to current email and verify ownership.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="2">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h4>Identity Check</h4>
                            <p>Enter OTP from old email to prove identity.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="3">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h4>New Email OTP</h4>
                            <p>Enter new email and send OTP to verify it.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="4">
                        <div class="step-number">4</div>
                        <div class="step-content">
                            <h4>Verify New</h4>
                            <p>Enter OTP received on new email address.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="5">
                        <div class="step-number">5</div>
                        <div class="step-content">
                            <h4>Confirm</h4>
                            <p>Final confirmation to complete email change.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Unbind Form with Step Guide -->
        <div id="unbindForm" class="form-wrapper">
            <div class="form-layout">
                <div class="form-card">
                    <h2 class="form-title"><i class="fas fa-unlink"></i> Unbind Email</h2>
                    
                    <div id="unbind-step1" class="step-content-form active">
                        <div class="form-group">
                            <label>Access Token</label>
                            <div class="input-wrapper">
                                <i class="fas fa-key input-icon"></i>
                                <input type="text" id="unbind_token" placeholder="Paste access token">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Current Email</label>
                            <div class="input-wrapper">
                                <i class="fas fa-envelope input-icon"></i>
                                <input type="email" id="unbind_email" placeholder="Enter current email">
                            </div>
                        </div>
                        <button class="btn" onclick="unbindStep1()">
                            <i class="fas fa-paper-plane"></i> Send OTP
                        </button>
                    </div>

                    <div id="unbind-step2" class="step-content-form">
                        <div class="form-group">
                            <label>OTP Code</label>
                            <div class="input-wrapper">
                                <i class="fas fa-shield-alt input-icon"></i>
                                <input type="text" id="unbind_otp" placeholder="Enter OTP">
                            </div>
                        </div>
                        <button class="btn" onclick="unbindStep2()">
                            <i class="fas fa-check"></i> Verify
                        </button>
                    </div>

                    <div id="unbind-step3" class="step-content-form">
                        <button class="btn btn-success" onclick="unbindStep3()">
                            <i class="fas fa-unlink"></i> Confirm Unbind
                        </button>
                    </div>

                    <div id="unbind_result" class="result-box">
                        <div class="result-header"></div>
                        <div class="result-content"></div>
                    </div>
                </div>

                <div class="guide-box">
                    <div class="guide-title"><i class="fas fa-list-ol"></i> Step Guide</div>
                    <div class="guide-step active" data-step="1">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h4>Send OTP</h4>
                            <p>Send verification code to current email.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="2">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h4>Verify</h4>
                            <p>Enter OTP to verify your identity.</p>
                        </div>
                    </div>
                    <div class="guide-step" data-step="3">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h4>Confirm Unbind</h4>
                            <p>Click confirm to remove email from account.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Simple Forms (No guide needed) -->
        <div id="cancelForm" class="form-wrapper">
            <div class="form-card" style="max-width: 600px; margin: 0 auto;">
                <h2 class="form-title"><i class="fas fa-ban"></i> Cancel Request</h2>
                <div class="form-group">
                    <label>Access Token</label>
                    <div class="input-wrapper">
                        <i class="fas fa-key input-icon"></i>
                        <input type="text" id="cancel_token" placeholder="Enter access token">
                    </div>
                </div>
                <button class="btn btn-success" onclick="cancelRequest()">
                    <i class="fas fa-ban"></i> Cancel Pending Request
                </button>
                <div id="cancel_result" class="result-box">
                    <div class="result-header"></div>
                    <div class="result-content"></div>
                </div>
            </div>
        </div>

        <div id="infoForm" class="form-wrapper">
            <div class="form-card" style="max-width: 600px; margin: 0 auto;">
                <h2 class="form-title"><i class="fas fa-info-circle"></i> Bind Information</h2>
                <div class="form-group">
                    <label>Access Token</label>
                    <div class="input-wrapper">
                        <i class="fas fa-key input-icon"></i>
                        <input type="text" id="info_token" placeholder="Enter access token">
                    </div>
                </div>
                <button class="btn" onclick="getBindInfo()">
                    <i class="fas fa-search"></i> Get Info
                </button>
                <div id="info_result" class="result-box">
                    <div class="result-header"></div>
                    <div class="result-content"></div>
                </div>
            </div>
        </div>

        <div id="eatForm" class="form-wrapper">
            <div class="form-card" style="max-width: 600px; margin: 0 auto;">
                <h2 class="form-title"><i class="fas fa-key"></i> EAT Converter</h2>
                <div class="form-group">
                    <label>EAT Token</label>
                    <div class="input-wrapper">
                        <i class="fas fa-lock input-icon"></i>
                        <input type="text" id="eat_token" placeholder="Enter EAT token">
                    </div>
                </div>
                <button class="btn" onclick="convertEAT()">
                    <i class="fas fa-exchange-alt"></i> Convert to Access Token
                </button>
                <div id="eat_result" class="result-box">
                    <div class="result-header"></div>
                    <div class="result-content"></div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let currentForm = null;
        let tempData = {};

        function showToast(title, message, type = 'success') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} toast-icon"></i>
                <div class="toast-content">
                    <div class="toast-title">${title}</div>
                    <div class="toast-message">${message}</div>
                </div>
            `;
            container.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        }

        function showForm(formId) {
            document.getElementById('dashboard').style.display = 'none';
            document.querySelectorAll('.form-wrapper').forEach(f => f.style.display = 'none');
            document.getElementById(formId + 'Form').style.display = 'block';
            document.getElementById('backBtn').classList.remove('hidden');
            currentForm = formId;
            resetForm(formId);
        }

        function goBack() {
            document.getElementById('dashboard').style.display = 'grid';
            document.querySelectorAll('.form-wrapper').forEach(f => f.style.display = 'none');
            document.getElementById('backBtn').classList.add('hidden');
            currentForm = null;
        }

        function resetForm(formId) {
            // Reset steps
            document.querySelectorAll(`#${formId}Form .step-content-form`).forEach((el, i) => {
                el.classList.toggle('active', i === 0);
            });
            
            // Reset guide
            document.querySelectorAll(`#${formId}Form .guide-step`).forEach((el, i) => {
                el.classList.remove('active', 'completed');
                if (i === 0) el.classList.add('active');
            });
            
            // Hide results
            const result = document.getElementById(formId + '_result');
            if (result) {
                result.classList.remove('show', 'success', 'error');
            }
            
            // Clear inputs
            document.querySelectorAll(`#${formId}Form input`).forEach(i => i.value = '');
        }

        function showStep(formId, stepNum) {
            // Hide all steps
            document.querySelectorAll(`#${formId}Form .step-content-form`).forEach(el => {
                el.classList.remove('active');
            });
            
            // Show current step
            document.getElementById(`${formId}-step${stepNum}`).classList.add('active');
            
            // Update guide
            document.querySelectorAll(`#${formId}Form .guide-step`).forEach(el => {
                const step = parseInt(el.dataset.step);
                el.classList.remove('active', 'completed');
                if (step === stepNum) el.classList.add('active');
                else if (step < stepNum) el.classList.add('completed');
            });
        }

        function setLoading(btn, loading) {
            if (loading) {
                btn.dataset.html = btn.innerHTML;
                btn.innerHTML = '<span class="spinner"></span> Processing...';
                btn.disabled = true;
            } else {
                btn.innerHTML = btn.dataset.html;
                btn.disabled = false;
            }
        }

        function showResult(formId, data, isError = false) {
            const box = document.getElementById(formId + '_result');
            const header = box.querySelector('.result-header');
            const content = box.querySelector('.result-content');
            
            box.classList.remove('success', 'error');
            box.classList.add(isError ? 'error' : 'success', 'show');
            
            header.innerHTML = isError 
                ? '<i class="fas fa-exclamation-circle"></i> Error'
                : '<i class="fas fa-check-circle"></i> Success';
            
            content.textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
        }

        // API Functions (same as before)
        async function bindStep1() {
            const token = document.getElementById('bind_token').value.trim();
            const email = document.getElementById('bind_email').value.trim();
            
            if (!token || !email) return showToast('Error', 'Fill all fields', 'error');
            
            const btn = document.querySelector('#bind-step1 .btn');
            setLoading(btn, true);
            
            try {
                const res = await fetch('/api/bind/send_otp', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({access_token: token, email: email})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.bind_token = token;
                    tempData.bind_email = email;
                    showStep('bind', 2);
                    showToast('OTP Sent', 'Check your email inbox');
                } else {
                    showResult('bind', data, true);
                    showToast('Failed', data.error, 'error');
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            } finally {
                setLoading(btn, false);
            }
        }

        async function bindStep2() {
            const otp = document.getElementById('bind_otp').value.trim();
            if (!otp) return showToast('Error', 'Enter OTP', 'error');
            
            const btn = document.querySelector('#bind-step2 .btn');
            setLoading(btn, true);
            
            try {
                const res = await fetch('/api/bind/verify_otp', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({otp: otp})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.bind_verifier = data.verifier_token;
                    showStep('bind', 3);
                    showToast('Verified', 'OTP is correct');
                } else {
                    showResult('bind', data, true);
                    showToast('Failed', data.error, 'error');
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            } finally {
                setLoading(btn, false);
            }
        }

        async function bindStep3() {
            const secondary = document.getElementById('bind_secondary').value.trim();
            const btn = document.querySelector('#bind-step3 .btn');
            setLoading(btn, true);
            
            try {
                const res = await fetch('/api/bind/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({secondary_password: secondary})
                });
                const data = await res.json();
                
                showResult('bind', data, !data.success);
                if (data.success) {
                    showToast('Success', 'Email bound successfully!');
                    setTimeout(() => resetForm('bind'), 2000);
                } else {
                    showToast('Failed', data.error, 'error');
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            } finally {
                setLoading(btn, false);
            }
        }

        async function changeStep1() {
            const token = document.getElementById('change_token').value.trim();
            const oldEmail = document.getElementById('change_old_email').value.trim();
            
            if (!token || !oldEmail) return showToast('Error', 'Fill all fields', 'error');
            
            try {
                const res = await fetch('/api/change/send_otp_old', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({access_token: token, old_email: oldEmail})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.change_token = token;
                    tempData.change_old_email = oldEmail;
                    showStep('change', 2);
                    showToast('OTP Sent', 'Check old email');
                } else {
                    showResult('change', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function changeStep2() {
            const otp = document.getElementById('change_otp_old').value.trim();
            if (!otp) return showToast('Error', 'Enter OTP', 'error');
            
            try {
                const res = await fetch('/api/change/verify_identity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({otp: otp})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.change_identity = data.identity_token;
                    showStep('change', 3);
                    showToast('Verified', 'Identity confirmed');
                } else {
                    showResult('change', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function changeStep3() {
            const newEmail = document.getElementById('change_new_email').value.trim();
            if (!newEmail) return showToast('Error', 'Enter new email', 'error');
            
            try {
                const res = await fetch('/api/change/send_otp_new', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_email: newEmail})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.change_new_email = newEmail;
                    showStep('change', 4);
                    showToast('OTP Sent', 'Check new email');
                } else {
                    showResult('change', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function changeStep4() {
            const otp = document.getElementById('change_otp_new').value.trim();
            if (!otp) return showToast('Error', 'Enter OTP', 'error');
            
            try {
                const res = await fetch('/api/change/verify_otp_new', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({otp: otp})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.change_verifier = data.verifier_token;
                    showStep('change', 5);
                    showToast('Verified', 'New email confirmed');
                } else {
                    showResult('change', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function changeStep5() {
            try {
                const res = await fetch('/api/change/confirm', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await res.json();
                
                showResult('change', data, !data.success);
                if (data.success) {
                    showToast('Success', 'Email changed!');
                    setTimeout(() => resetForm('change'), 2000);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function unbindStep1() {
            const token = document.getElementById('unbind_token').value.trim();
            const email = document.getElementById('unbind_email').value.trim();
            
            if (!token || !email) return showToast('Error', 'Fill all fields', 'error');
            
            try {
                const res = await fetch('/api/unbind/send_otp', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({access_token: token, email: email})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.unbind_token = token;
                    tempData.unbind_email = email;
                    showStep('unbind', 2);
                    showToast('OTP Sent', 'Check email');
                } else {
                    showResult('unbind', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function unbindStep2() {
            const otp = document.getElementById('unbind_otp').value.trim();
            if (!otp) return showToast('Error', 'Enter OTP', 'error');
            
            try {
                const res = await fetch('/api/unbind/verify_identity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({otp: otp})
                });
                const data = await res.json();
                
                if (data.success) {
                    tempData.unbind_identity = data.identity_token;
                    showStep('unbind', 3);
                    showToast('Verified', 'Identity confirmed');
                } else {
                    showResult('unbind', data, true);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function unbindStep3() {
            try {
                const res = await fetch('/api/unbind/confirm', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await res.json();
                
                showResult('unbind', data, !data.success);
                if (data.success) {
                    showToast('Success', 'Email unbound!');
                    setTimeout(() => resetForm('unbind'), 2000);
                }
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function cancelRequest() {
            const token = document.getElementById('cancel_token').value.trim();
            if (!token) return showToast('Error', 'Enter token', 'error');
            
            try {
                const res = await fetch('/api/cancel', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({access_token: token})
                });
                const data = await res.json();
                
                showResult('cancel', data, !data.success);
                if (data.success) showToast('Success', 'Request cancelled!');
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function getBindInfo() {
            const token = document.getElementById('info_token').value.trim();
            if (!token) return showToast('Error', 'Enter token', 'error');
            
            try {
                const res = await fetch(`/api/bind_info?access_token=${encodeURIComponent(token)}`);
                const data = await res.json();
                
                showResult('info', data, data.error);
                if (!data.error) showToast('Success', 'Info retrieved');
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        async function convertEAT() {
            const eat = document.getElementById('eat_token').value.trim();
            if (!eat) return showToast('Error', 'Enter EAT', 'error');
            
            try {
                const res = await fetch('/api/eat_to_access', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({eat_token: eat})
                });
                const data = await res.json();
                
                showResult('eat', data, !data.success);
                if (data.success) showToast('Success', 'Token converted!');
            } catch (err) {
                showToast('Error', err.message, 'error');
            }
        }

        // Swipe back gesture for mobile
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        document.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
        
        function handleSwipe() {
            if (touchEndX > touchStartX + 100 && currentForm) {
                // Swipe right to go back
                goBack();
            }
        }
    </script>

    <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js', { scope: '/' })
    }
    </script>

</body>
</html>
"""

# [All API routes remain the same as previous version]
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
    
@app.route('/sw.js')
def sw():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/api/bind/send_otp', methods=['POST'])
def api_bind_send_otp():
    data = request.json
    access_token = data.get('access_token')
    email = data.get('email')
    if not access_token or not email:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    api = GarenaAPI(access_token)
    success, result = api.send_otp(email)
    if success:
        session['bind_access_token'] = access_token
        session['bind_email'] = email
        return jsonify({'success': True, 'message': 'OTP sent'})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/bind/verify_otp', methods=['POST'])
def api_bind_verify_otp():
    data = request.json
    otp = data.get('otp')
    access_token = session.get('bind_access_token')
    email = session.get('bind_email')
    if not access_token or not email:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.verify_otp(otp, email)
    if success:
        session['bind_verifier_token'] = result
        return jsonify({'success': True, 'verifier_token': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/bind/create', methods=['POST'])
def api_bind_create():
    data = request.json
    secondary = data.get('secondary_password')
    access_token = session.get('bind_access_token')
    email = session.get('bind_email')
    verifier_token = session.get('bind_verifier_token')
    if not all([access_token, email, verifier_token]):
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.create_bind_request(verifier_token, email, secondary)
    if success:
        for key in ['bind_access_token', 'bind_email', 'bind_verifier_token']:
            session.pop(key, None)
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/change/send_otp_old', methods=['POST'])
def api_change_send_otp_old():
    data = request.json
    access_token = data.get('access_token')
    old_email = data.get('old_email')
    if not access_token or not old_email:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    api = GarenaAPI(access_token)
    success, result = api.send_otp(old_email)
    if success:
        session['change_access_token'] = access_token
        session['change_old_email'] = old_email
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/change/verify_identity', methods=['POST'])
def api_change_verify_identity():
    data = request.json
    otp = data.get('otp')
    access_token = session.get('change_access_token')
    email = session.get('change_old_email')
    if not access_token or not email:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.verify_identity(email, otp)
    if success:
        session['change_identity_token'] = result
        return jsonify({'success': True, 'identity_token': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/change/send_otp_new', methods=['POST'])
def api_change_send_otp_new():
    data = request.json
    new_email = data.get('new_email')
    access_token = session.get('change_access_token')
    if not access_token:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.send_otp(new_email)
    if success:
        session['change_new_email'] = new_email
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/change/verify_otp_new', methods=['POST'])
def api_change_verify_otp_new():
    data = request.json
    otp = data.get('otp')
    access_token = session.get('change_access_token')
    new_email = session.get('change_new_email')
    if not access_token or not new_email:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.verify_otp(otp, new_email)
    if success:
        session['change_verifier_token'] = result
        return jsonify({'success': True, 'verifier_token': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/change/confirm', methods=['POST'])
def api_change_confirm():
    access_token = session.get('change_access_token')
    identity_token = session.get('change_identity_token')
    new_email = session.get('change_new_email')
    verifier_token = session.get('change_verifier_token')
    if not all([access_token, identity_token, new_email, verifier_token]):
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.create_rebind_request(identity_token, new_email, verifier_token)
    if success:
        for key in ['change_access_token', 'change_old_email', 'change_identity_token', 'change_new_email', 'change_verifier_token']:
            session.pop(key, None)
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/unbind/send_otp', methods=['POST'])
def api_unbind_send_otp():
    data = request.json
    access_token = data.get('access_token')
    email = data.get('email')
    if not access_token or not email:
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    api = GarenaAPI(access_token)
    success, result = api.send_otp(email)
    if success:
        session['unbind_access_token'] = access_token
        session['unbind_email'] = email
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/unbind/verify_identity', methods=['POST'])
def api_unbind_verify_identity():
    data = request.json
    otp = data.get('otp')
    access_token = session.get('unbind_access_token')
    email = session.get('unbind_email')
    if not access_token or not email:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.verify_identity(email, otp)
    if success:
        session['unbind_identity_token'] = result
        return jsonify({'success': True, 'identity_token': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/unbind/confirm', methods=['POST'])
def api_unbind_confirm():
    access_token = session.get('unbind_access_token')
    identity_token = session.get('unbind_identity_token')
    if not access_token or not identity_token:
        return jsonify({'success': False, 'error': 'Session expired'}), 400
    api = GarenaAPI(access_token)
    success, result = api.create_unbind_request(identity_token)
    if success:
        for key in ['unbind_access_token', 'unbind_email', 'unbind_identity_token']:
            session.pop(key, None)
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/cancel', methods=['POST'])
def api_cancel():
    data = request.json
    access_token = data.get('access_token')
    if not access_token:
        return jsonify({'success': False, 'error': 'Missing token'}), 400
    api = GarenaAPI(access_token)
    success, result = api.cancel_request()
    if success:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/bind_info', methods=['GET'])
def api_bind_info():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({'success': False, 'error': 'Missing token'}), 400
    success, result = get_bind_info(access_token)
    if success:
        return jsonify(result)
    return jsonify({'success': False, 'error': result}), 400

@app.route('/api/eat_to_access', methods=['POST'])
def api_eat_to_access():
    data = request.json
    eat_token = data.get('eat_token')
    if not eat_token:
        return jsonify({'success': False, 'error': 'Missing EAT'}), 400
    success, result = convert_eat_to_access(eat_token)
    if success:
        return jsonify(result)
    return jsonify({'success': False, 'error': result}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)