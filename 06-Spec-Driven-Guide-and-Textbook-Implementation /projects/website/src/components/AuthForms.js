/**
 * Auth Forms Component
 * Signup and Login forms for user authentication
 */

import React, { useState } from 'react';

interface AuthFormsProps {
  apiBaseUrl?: string;
  onLoginSuccess?: () => void;
  onSignupSuccess?: () => void;
}

type AuthMode = 'login' | 'signup';

interface FormData {
  email: string;
  password: string;
  confirmPassword?: string;
  background?: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

const BACKGROUND_OPTIONS = [
  { value: 'beginner', label: 'Beginner - New to AI/DevOps' },
  { value: 'engineer', label: 'Engineer - Some technical experience' },
  { value: 'architect', label: 'Architect - Designs systems' },
  { value: 'manager', label: 'Manager - Leads teams' },
];

export default function AuthForms({
  apiBaseUrl = 'http://localhost:8000',
  onLoginSuccess,
  onSignupSuccess,
}: AuthFormsProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirmPassword: '',
    background: 'engineer',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (mode === 'signup') {
      if (formData.confirmPassword !== formData.password) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});
    setSuccessMessage(null);

    const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/signup';
    const body = mode === 'login'
      ? { email: formData.email, password: formData.password }
      : { email: formData.email, password: formData.password };

    try {
      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      setSuccessMessage(mode === 'login' ? 'Login successful!' : 'Account created successfully!');

      // Reset form
      setFormData({
        email: '',
        password: '',
        confirmPassword: '',
        background: 'engineer',
      });

      // Callbacks
      if (mode === 'login' && onLoginSuccess) {
        onLoginSuccess();
      } else if (mode === 'signup' && onSignupSuccess) {
        onSignupSuccess();
      }

      // Redirect or reload after successful auth
      setTimeout(() => {
        window.location.reload();
      }, 1000);

    } catch (err) {
      setErrors({
        general: err instanceof Error ? err.message : 'Authentication failed',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear field error on change
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login');
    setErrors({});
    setSuccessMessage(null);
  };

  return (
    <div className="auth-forms-container">
      <div className="auth-forms-card">
        <h2 className="auth-title">
          {mode === 'login' ? 'Welcome Back' : 'Create Account'}
        </h2>
        <p className="auth-subtitle">
          {mode === 'login'
            ? 'Sign in to personalize your learning experience'
            : 'Join to track your progress and get personalized content'}
        </p>

        {successMessage && (
          <div className="auth-success">
            ✓ {successMessage}
          </div>
        )}

        {errors.general && (
          <div className="auth-error">
            ⚠️ {errors.general}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="you@example.com"
              disabled={isLoading}
              autoComplete="email"
            />
            {errors.email && (
              <span className="field-error">{errors.email}</span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              disabled={isLoading}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
            {errors.password && (
              <span className="field-error">{errors.password}</span>
            )}
          </div>

          {/* Confirm Password (signup only) */}
          {mode === 'signup' && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                disabled={isLoading}
                autoComplete="new-password"
              />
              {errors.confirmPassword && (
                <span className="field-error">{errors.confirmPassword}</span>
              )}
            </div>
          )}

          {/* Background (signup only) */}
          {mode === 'signup' && (
            <div className="form-group">
              <label htmlFor="background">Your Background</label>
              <select
                id="background"
                name="background"
                value={formData.background}
                onChange={handleInputChange}
                disabled={isLoading}
              >
                {BACKGROUND_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <span className="field-hint">
                This helps us personalize content for you
              </span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="auth-submit-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner-small" />
                {mode === 'login' ? 'Signing in...' : 'Creating account...'}
              </>
            ) : (
              mode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="auth-toggle">
          <span>
            {mode === 'login'
              ? "Don't have an account?"
              : 'Already have an account?'}
          </span>
          <button
            type="button"
            className="auth-toggle-button"
            onClick={toggleMode}
            disabled={isLoading}
          >
            {mode === 'login' ? 'Sign Up' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}