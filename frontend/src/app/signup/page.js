"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { SIGNUP_API_URL } from "../constants";
import { useAuth } from "../contexts/AuthContext";

export default function Signup() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [passwordStrength, setPasswordStrength] = useState("");
  const router = useRouter();
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(""); // Clear error when user starts typing
    
    // Check password strength
    if (e.target.name === "password") {
      checkPasswordStrength(e.target.value);
    }
  };

  const checkPasswordStrength = (password) => {
    if (password.length === 0) {
      setPasswordStrength("");
      return;
    }
    
    let strength = 0;
    let feedback = [];
    
    if (password.length >= 8) strength++;
    else feedback.push("at least 8 characters");
    
    if (/[A-Z]/.test(password)) strength++;
    else feedback.push("one uppercase letter");
    
    if (/[a-z]/.test(password)) strength++;
    else feedback.push("one lowercase letter");
    
    if (/\d/.test(password)) strength++;
    else feedback.push("one number");
    
    if (strength === 4) {
      setPasswordStrength("Strong password ✓");
    } else if (strength >= 2) {
      setPasswordStrength(`Weak - needs ${feedback.join(", ")}`);
    } else {
      setPasswordStrength(`Very weak - needs ${feedback.join(", ")}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Client-side validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      setIsLoading(false);
      return;
    }

    try {
      const response = await axios.post(SIGNUP_API_URL, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      
      if (response.data.status === "success") {
        // Use auth context to login
        login(response.data.user, response.data.token);
        
        // Redirect to main chat page
        router.push("/");
      }
    } catch (error) {
      console.error("Signup error:", error);
      setError(
        error.response?.data?.message || 
        "Signup failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#131314] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-medium text-gray-400 bg-gradient-to-r from-cyan-400 via-violet-500 to-lime-400 bg-clip-text text-transparent mb-2">
            Create Account
          </h1>
          <p className="text-gray-500">Join the MeTTa community</p>
        </div>

        {/* Signup Form */}
        <div className="bg-[#1a1a1a] rounded-xl shadow-lg border border-gray-700 p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                minLength={3}
                className="w-full px-4 py-3 bg-[#1f1f1f] border border-gray-600 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition duration-200"
                placeholder="Choose a username (min 3 characters)"
                disabled={isLoading}
              />
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1f1f1f] border border-gray-600 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition duration-200"
                placeholder="Enter your email address"
                disabled={isLoading}
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-4 py-3 bg-[#1f1f1f] border border-gray-600 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition duration-200"
                placeholder="Create a strong password"
                disabled={isLoading}
              />
              {passwordStrength && (
                <p className={`mt-1 text-xs ${
                  passwordStrength.includes("Strong") ? "text-green-400" : 
                  passwordStrength.includes("Weak") ? "text-yellow-400" : 
                  "text-red-400"
                }`}>
                  {passwordStrength}
                </p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1f1f1f] border border-gray-600 rounded-lg text-gray-300 placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition duration-200"
                placeholder="Confirm your password"
                disabled={isLoading}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-900/20 border border-red-700 rounded-lg p-3">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !formData.username || !formData.email || !formData.password || !formData.confirmPassword}
              className={`w-full py-3 px-4 rounded-lg font-medium transition duration-200 ${
                isLoading || !formData.username || !formData.email || !formData.password || !formData.confirmPassword
                  ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-cyan-500 to-violet-500 text-white hover:from-cyan-600 hover:to-violet-600 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-[#131314]"
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Creating Account...
                </div>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Already have an account?{" "}
              <button
                onClick={() => router.push("/login")}
                className="text-cyan-400 hover:text-cyan-300 font-medium transition duration-200"
              >
                Sign in here
              </button>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-600 text-xs">
            MeTTa Self-Reflective RAG System
          </p>
        </div>
      </div>
    </div>
  );
}
