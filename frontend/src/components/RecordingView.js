import React, { useState, useEffect, useRef } from 'react';
import { Button, Card, Typography, Space, message } from 'antd';
import { AudioOutlined, PauseOutlined, StopOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import WaveformAnimation from './WaveformAnimation';
import './RecordingView.css';

const { Title, Paragraph } = Typography;

function RecordingView({ recording, onRecordingComplete }) {
  const { token, API_URL } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [chunkIndex, setChunkIndex] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          
          // Upload chunk to backend
          const blob = new Blob([event.data], { type: 'audio/webm' });
          await uploadChunk(blob, chunkIndex);
          setChunkIndex(prev => prev + 1);
        }
      };

      // Create chunks every 10 seconds
      mediaRecorder.start(10000);
      setIsRecording(true);
      message.success('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      message.error('Failed to access microphone');
    }
  };

  const uploadChunk = async (blob, index) => {
    if (!recording) return;

    const formData = new FormData();
    formData.append('audio_chunk', blob, `chunk_${index}.webm`);
    formData.append('chunk_index', index);

    try {
      await axios.post(
        `${API_URL}/recordings/${recording.id}/chunks`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
    } catch (error) {
      console.error('Failed to upload chunk:', error);
    }
  };

  const pauseRecording = async () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);

      try {
        await axios.patch(
          `${API_URL}/recordings/${recording.id}/pause`,
          {},
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        message.info('Recording paused');
      } catch (error) {
        console.error('Failed to pause recording:', error);
      }
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      message.info('Recording resumed');
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      // Finish recording on backend
      try {
        message.loading('Processing transcription...', 0);
        await axios.post(
          `${API_URL}/recordings/${recording.id}/finish`,
          {},
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        message.destroy();
        message.success('Recording completed and transcribed');
        onRecordingComplete();
      } catch (error) {
        message.destroy();
        console.error('Failed to finish recording:', error);
        message.error('Failed to finish recording');
      }
    }
  };

  if (!recording) {
    return (
      <div className="recording-view-empty">
        <AudioOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
        <Title level={3} style={{ color: '#8c8c8c', marginTop: 16 }}>
          Select or create a recording to begin
        </Title>
      </div>
    );
  }

  return (
    <div className="recording-view">
      <Card>
        <Title level={3}>Recording Session</Title>
        <Paragraph>Status: <strong>{recording.status}</strong></Paragraph>

        {recording.status === 'active' && !isRecording && (
          <Space>
            <Button
              type="primary"
              size="large"
              icon={<AudioOutlined />}
              onClick={startRecording}
            >
              Start Recording
            </Button>
          </Space>
        )}

        {isRecording && (
          <div className="recording-controls">
            <WaveformAnimation />
            <Space style={{ marginTop: 24 }}>
              {!isPaused ? (
                <Button
                  size="large"
                  icon={<PauseOutlined />}
                  onClick={pauseRecording}
                >
                  Pause
                </Button>
              ) : (
                <Button
                  size="large"
                  icon={<AudioOutlined />}
                  onClick={resumeRecording}
                >
                  Resume
                </Button>
              )}
              <Button
                size="large"
                danger
                icon={<StopOutlined />}
                onClick={stopRecording}
              >
                End Recording
              </Button>
            </Space>
          </div>
        )}

        {recording.status === 'ended' && recording.transcription_text && (
          <div className="transcription-section">
            <Title level={4}>Transcription</Title>
            <Card className="transcription-card">
              <Paragraph>{recording.transcription_text}</Paragraph>
            </Card>
          </div>
        )}
      </Card>
    </div>
  );
}

export default RecordingView;