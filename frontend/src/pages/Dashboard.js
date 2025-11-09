import React, { useState, useEffect } from 'react';
import { Layout, Avatar, Dropdown, Menu, message } from 'antd';
import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import RecordingList from '../components/RecordingList';
import RecordingView from '../components/RecordingView';
import axios from 'axios';
import './Dashboard.css';

const { Header, Sider, Content } = Layout;

function Dashboard() {
  const { user, logout, token, API_URL } = useAuth();
  const navigate = useNavigate();
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch recordings on mount
  useEffect(() => {
    fetchRecordings();
  }, []);

  const fetchRecordings = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/recordings`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setRecordings(response.data);
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
      message.error('Failed to load recordings');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleRecordingSelect = (recording) => {
    setSelectedRecording(recording);
  };

  const handleRecordingComplete = () => {
    // Refresh recordings list
    fetchRecordings();
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        Logout
      </Menu.Item>
    </Menu>
  );

  return (
    <Layout className="dashboard-layout">
      <Header className="dashboard-header">
        <div className="header-title">Audio Transcription Service</div>
        <Dropdown overlay={userMenu} placement="bottomRight">
          <Avatar 
            src={user?.avatar_url} 
            icon={<UserOutlined />}
            className="user-avatar"
          />
        </Dropdown>
      </Header>
      <Layout>
        <Sider width={300} className="dashboard-sider">
          <RecordingList
            recordings={recordings}
            loading={loading}
            onSelect={handleRecordingSelect}
            selectedRecording={selectedRecording}
          />
        </Sider>
        <Content className="dashboard-content">
          <RecordingView
            recording={selectedRecording}
            onRecordingComplete={handleRecordingComplete}
          />
        </Content>
        <Sider width={250} className="dashboard-sider-right">
          <div className="metadata-panel">
            <h3>Metadata</h3>
            <p>Additional information and notes will appear here.</p>
          </div>
        </Sider>
      </Layout>
    </Layout>
  );
}

export default Dashboard;