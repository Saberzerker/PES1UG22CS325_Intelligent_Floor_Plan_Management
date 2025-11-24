import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect(token) {
    if (this.socket) return;

    this.socket = io('http://localhost:8000', {
      auth: { token },
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      this.isConnected = true;
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      this.isConnected = false;
      console.log('WebSocket disconnected');
    });

    this.socket.on('notification', (data) => {
      // Handle notifications
      console.log('Notification:', data);
    });

    this.socket.on('floor_plan_update', (data) => {
      // Handle floor plan updates
      console.log('Floor plan update:', data);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinFloorPlan(floorPlanId) {
    if (this.socket) {
      this.socket.emit('join_floor_plan', { floor_plan_id: floorPlanId });
    }
  }

  leaveFloorPlan(floorPlanId) {
    if (this.socket) {
      this.socket.emit('leave_floor_plan', { floor_plan_id: floorPlanId });
    }
  }

  sendMessage(room, message) {
    if (this.socket) {
      this.socket.emit('send_message', { room, message });
    }
  }

  onNotification(callback) {
    if (this.socket) {
      this.socket.on('notification', callback);
    }
  }

  onFloorPlanUpdate(callback) {
    if (this.socket) {
      this.socket.on('floor_plan_update', callback);
    }
  }
}

export default new WebSocketService();