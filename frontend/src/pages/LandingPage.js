import React from 'react';
import { Button, Typography } from 'antd';
import { GoogleOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const { Title, Paragraph } = Typography;

function LandingPage() {
  const { token, API_URL } = useAuth();
  const navigate = useNavigate();

  // Redirect to dashboard if already logged in
  React.useEffect(() => {
    if (token) {
      navigate('/dashboard');
    }
  }, [token, navigate]);

  const handleGoogleLogin = () => {
    // Redirect to backend Google OAuth endpoint
    window.location.href = `${API_URL}/auth/google/login`;
  };

  return (
    <div className="landing-page">
      <div className="landing-overlay">
        <div className="landing-content">
          <Title level={1} className="landing-title">
            Audio Transcription Service
          </Title>
          <Paragraph className="landing-subtitle">
            Professional healthcare transcription powered by AI
          </Paragraph>
          <Paragraph className="landing-description">
            Record patient notes, dictate observations, and receive accurate transcriptions
            instantly. Designed for healthcare professionals who value efficiency and accuracy.
          </Paragraph>
          <Button
            type="primary"
            size="large"
            icon={<GoogleOutlined />}
            onClick={handleGoogleLogin}
            className="google-login-button"
          >
            Login with Google
          </Button>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;