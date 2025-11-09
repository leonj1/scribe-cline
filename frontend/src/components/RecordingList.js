import React from 'react';
import { List, Button, Spin, Empty } from 'antd';
import { PlusOutlined, AudioOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './RecordingList.css';

function RecordingList({ recordings, loading, onSelect, selectedRecording }) {
  const { token, API_URL } = useAuth();
  const [creating, setCreating] = React.useState(false);

  const handleNewRecording = async () => {
    setCreating(true);
    try {
      const response = await axios.post(`${API_URL}/recordings`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      onSelect(response.data);
    } catch (error) {
      console.error('Failed to create recording:', error);
    } finally {
      setCreating(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#52c41a';
      case 'paused':
        return '#faad14';
      case 'ended':
        return '#1890ff';
      default:
        return '#d9d9d9';
    }
  };

  return (
    <div className="recording-list">
      <Button
        type="primary"
        icon={<PlusOutlined />}
        onClick={handleNewRecording}
        loading={creating}
        block
        style={{ marginBottom: 16 }}
      >
        New Recording
      </Button>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin />
        </div>
      ) : recordings.length === 0 ? (
        <Empty description="No recordings yet" />
      ) : (
        <List
          dataSource={recordings}
          renderItem={(recording) => (
            <List.Item
              className={`recording-item ${selectedRecording?.id === recording.id ? 'selected' : ''}`}
              onClick={() => onSelect(recording)}
            >
              <div className="recording-item-content">
                <div className="recording-header">
                  <AudioOutlined style={{ marginRight: 8, color: getStatusColor(recording.status) }} />
                  <span className="recording-status">{recording.status}</span>
                </div>
                <div className="recording-date">{formatDate(recording.created_at)}</div>
                {recording.transcription_text && (
                  <div className="recording-preview">
                    {recording.transcription_text.substring(0, 50)}...
                  </div>
                )}
              </div>
            </List.Item>
          )}
        />
      )}
    </div>
  );
}

export default RecordingList;