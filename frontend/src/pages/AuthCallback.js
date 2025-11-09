import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../context/AuthContext';

function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    // Extract token from URL query parameters
    const params = new URLSearchParams(location.search);
    const token = params.get('token');

    if (token) {
      login(token);
      navigate('/dashboard');
    } else {
      // If no token, redirect to landing page
      navigate('/');
    }
  }, [location, login, navigate]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh' 
    }}>
      <Spin size="large" tip="Authenticating..." />
    </div>
  );
}

export default AuthCallback;