/**
 * Login Page
 * Authentication page with login/signup forms
 */

import React from 'react';
import Layout from '@theme/Layout';
import AuthForms from '../components/AuthForms';

export default function LoginPage() {
  const apiBaseUrl = typeof window !== 'undefined'
    ? (window.__BACKEND_URL__ || 'http://localhost:8000')
    : 'http://localhost:8000';

  const handleSuccess = () => {
    // Redirect to profile after successful authentication
    window.location.href = '/profile';
  };

  return (
    <Layout title="Sign In">
      <div className="login-page-container">
        <div className="login-page-content">
          <AuthForms
            apiBaseUrl={apiBaseUrl}
            onLoginSuccess={handleSuccess}
            onSignupSuccess={handleSuccess}
          />
        </div>
      </div>
    </Layout>
  );
}