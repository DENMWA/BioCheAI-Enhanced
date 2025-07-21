import { io, Socket } from 'socket.io-client';

const WEBSOCKET_URL = (import.meta as any).env.VITE_WEBSOCKET_URL || 'http://localhost:5000';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect(_userId: number): void {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(WEBSOCKET_URL, {
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('user_joined', (data) => {
      this.emit('user_joined', data);
    });

    this.socket.on('user_left', (data) => {
      this.emit('user_left', data);
    });

    this.socket.on('analysis_updated', (data) => {
      this.emit('analysis_updated', data);
    });

    this.socket.on('comment_received', (data) => {
      this.emit('comment_received', data);
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinSession(sessionId: string, userId: number): void {
    if (this.socket) {
      this.socket.emit('join_session', { session_id: sessionId, user_id: userId });
    }
  }

  leaveSession(sessionId: string, userId: number): void {
    if (this.socket) {
      this.socket.emit('leave_session', { session_id: sessionId, user_id: userId });
    }
  }

  updateAnalysis(sessionId: string, analysisData: any, userId: number): void {
    if (this.socket) {
      this.socket.emit('analysis_update', {
        session_id: sessionId,
        analysis_data: analysisData,
        user_id: userId,
      });
    }
  }

  addComment(sessionId: string, commentData: any, userId: number): void {
    if (this.socket) {
      this.socket.emit('comment_added', {
        session_id: sessionId,
        comment_data: commentData,
        user_id: userId,
      });
    }
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data));
    }
  }
}

export const websocketService = new WebSocketService();
