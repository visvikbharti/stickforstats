import SockJS from 'sockjs-client';
import EventEmitter from 'events';
import { secureWebSocketUrl, getWebSocketProtocol } from '../utils/secureWebSocketUtils';

// Connection status constants
export const ConnectionStatus = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error'
};

/**
 * Browser Compatibility Detection
 */
const compatibilityCheck = {
  // Check if native WebSockets are supported
  hasNativeWebSocket: () => {
    return typeof WebSocket !== 'undefined';
  },
  
  // Check if SockJS is needed as a fallback
  needsSockJSFallback: () => {
    // Safari versions < 7 had incomplete WebSocket support
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    const safariVersion = isSafari ? parseInt(navigator.userAgent.match(/Version\/(\d+)/)?.[1] || '0', 10) : 0;
    
    // IE versions below 10 had no WebSocket support
    const isIE = /MSIE|Trident/.test(navigator.userAgent);
    
    return (isSafari && safariVersion < 7) || isIE;
  },
  
  // Check if browser supports binary WebSocket messages
  supportsBinaryMessages: () => {
    if (!compatibilityCheck.hasNativeWebSocket()) {
      return false;
    }
    
    // Some older browsers support WebSocket but not binary messages
    // This is a simplified check - production code would be more comprehensive
    const isOldBrowser = /MSIE 10/i.test(navigator.userAgent);
    return !isOldBrowser;
  },
  
  // Check if the browser supports the specific WebSocket subprotocols we use
  supportsSubprotocols: () => {
    // Most modern browsers support subprotocols, but there have been issues historically
    // with some versions of Safari
    return compatibilityCheck.hasNativeWebSocket() && !(/Version\/[7-9]/i.test(navigator.userAgent) && /Safari/i.test(navigator.userAgent));
  },
  
  // Get maximum recommended message size for this browser
  getMaxMessageSize: () => {
    // Mobile browsers might have tighter memory constraints
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Default to 64KB for desktop, 16KB for mobile
    return isMobile ? 16 * 1024 : 64 * 1024;
  }
};

/**
 * Enhanced WebSocket service with cross-browser compatibility
 * Provides fallbacks and reconnection logic
 */
class WebSocketService extends EventEmitter {
  constructor() {
    super();
    
    // Initialize properties
    this.socket = null;
    this.status = ConnectionStatus.DISCONNECTED;
    this.url = null;
    this.options = {};
    this.reconnectCount = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 1000; // Starting at 1 second
    this.reconnectTimer = null;
    this.pingInterval = null;
    this.fallbackMode = null;
    this.messageQueue = [];
    this.isConnecting = false;
    
    // Bind methods to preserve 'this' context
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.reconnect = this.reconnect.bind(this);
    this.send = this.send.bind(this);
    this.handleMessage = this.handleMessage.bind(this);
    this.handleOpen = this.handleOpen.bind(this);
    this.handleClose = this.handleClose.bind(this);
    this.handleError = this.handleError.bind(this);
  }
  
  /**
   * Connect to the WebSocket server with cross-browser compatibility
   * @param {string} url - The WebSocket server URL
   * @param {Object} options - Connection options
   * @param {string[]} [options.protocols] - WebSocket subprotocols
   * @param {boolean} [options.autoReconnect=true] - Whether to auto-reconnect
   * @param {number} [options.maxReconnectAttempts=10] - Maximum reconnection attempts
   * @param {number} [options.reconnectIntervalMs=1000] - Base reconnection interval (ms)
   * @param {boolean} [options.debug=false] - Enable debug logging
   * @param {boolean} [options.forceFallback=false] - Force using fallback (for testing)
   */
  connect(url, options = {}) {
    if (this.isConnecting) {
      console.warn('WebSocketService: Connection already in progress');
      return;
    }
    
    this.isConnecting = true;
    this.url = url;
    this.options = {
      protocols: [],
      autoReconnect: true,
      maxReconnectAttempts: 10,
      reconnectIntervalMs: 1000,
      debug: false,
      forceFallback: false,
      forceSecure: process.env.NODE_ENV === 'production', // Force secure in production
      ...options
    };
    
    this.maxReconnectAttempts = this.options.maxReconnectAttempts;
    this.reconnectInterval = this.options.reconnectIntervalMs;
    
    // Update status
    this._setStatus(ConnectionStatus.CONNECTING);
    
    // Choose connection strategy based on browser capabilities or forced fallback
    if (this.options.forceFallback || compatibilityCheck.needsSockJSFallback()) {
      this._connectWithSockJS();
    } else if (compatibilityCheck.hasNativeWebSocket()) {
      this._connectWithNativeWebSocket();
    } else {
      // Last resort - long polling via SockJS
      this._connectWithSockJS();
    }
  }
  
  /**
   * Connect using native WebSocket
   * @private
   */
  _connectWithNativeWebSocket() {
    try {
      if (this.options.debug) {
        console.log('WebSocketService: Connecting with native WebSocket');
      }
      
      // Use secure WebSocket URL
      const secureUrl = secureWebSocketUrl(this.url, this.options.forceSecure || process.env.NODE_ENV === 'production');
      
      if (this.options.debug) {
        console.log(`WebSocketService: Using ${secureUrl}`);
      }
      
      // Create WebSocket with optional protocols
      this.socket = this.options.protocols.length > 0 && compatibilityCheck.supportsSubprotocols()
        ? new WebSocket(secureUrl, this.options.protocols)
        : new WebSocket(secureUrl);
        
      this.fallbackMode = 'native';
      
      // Set event handlers
      this.socket.onopen = this.handleOpen;
      this.socket.onclose = this.handleClose;
      this.socket.onerror = this.handleError;
      this.socket.onmessage = this.handleMessage;
    } catch (error) {
      console.error('WebSocketService: Error creating native WebSocket', error);
      
      // Fall back to SockJS on error
      setTimeout(() => {
        this._connectWithSockJS();
      }, 100);
    }
  }
  
  /**
   * Connect using SockJS fallback
   * @private
   */
  _connectWithSockJS() {
    try {
      if (this.options.debug) {
        console.log('WebSocketService: Connecting with SockJS fallback');
      }
      
      // Use secure protocol based on environment
      const protocol = window.location.protocol === 'https:' || this.options.forceSecure || process.env.NODE_ENV === 'production' ? 'https://' : 'http://'; 
      
      // Adjust URL for SockJS
      const sockJsUrl = this.url.replace(/^(ws|wss):\/\//i, protocol);
      
      if (this.options.debug) {
        console.log(`WebSocketService: Using SockJS URL: ${sockJsUrl}`);
      }
      
      this.socket = new SockJS(sockJsUrl);
      this.fallbackMode = 'sockjs';
      
      // Set event handlers
      this.socket.onopen = this.handleOpen;
      this.socket.onclose = this.handleClose;
      this.socket.onerror = this.handleError;
      this.socket.onmessage = this.handleMessage;
    } catch (error) {
      console.error('WebSocketService: Error creating SockJS connection', error);
      this._setStatus(ConnectionStatus.ERROR);
      this.isConnecting = false;
      this.emit('error', new Error('Failed to establish connection with all available methods'));
    }
  }
  
  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.options.debug) {
      console.log('WebSocketService: Disconnecting');
    }
    
    this._clearTimers();
    
    if (this.socket) {
      // Different closing procedure based on connection type
      if (this.fallbackMode === 'native') {
        try {
          // Native WebSocket uses close code 1000 (normal closure)
          this.socket.close(1000, 'Client disconnect');
        } catch (e) {
          console.warn('WebSocketService: Error during disconnect', e);
        }
      } else if (this.fallbackMode === 'sockjs') {
        try {
          this.socket.close();
        } catch (e) {
          console.warn('WebSocketService: Error during SockJS disconnect', e);
        }
      }
      
      this.socket = null;
    }
    
    this._setStatus(ConnectionStatus.DISCONNECTED);
    this.isConnecting = false;
  }
  
  /**
   * Try to reconnect to the server with exponential backoff
   */
  reconnect() {
    if (this.reconnectCount >= this.maxReconnectAttempts) {
      if (this.options.debug) {
        console.log(`WebSocketService: Max reconnect attempts (${this.maxReconnectAttempts}) reached`);
      }
      this._setStatus(ConnectionStatus.ERROR);
      return;
    }
    
    this.reconnectCount++;
    
    // Calculate exponential backoff time
    const delay = Math.min(
      this.reconnectInterval * Math.pow(1.5, this.reconnectCount - 1),
      30000 // Max 30 seconds
    );
    
    if (this.options.debug) {
      console.log(`WebSocketService: Reconnecting in ${delay}ms (attempt ${this.reconnectCount}/${this.maxReconnectAttempts})`);
    }
    
    this._setStatus(ConnectionStatus.RECONNECTING);
    
    // Clear any existing timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    // Set reconnect timer
    this.reconnectTimer = setTimeout(() => {
      this.disconnect();
      this.connect(this.url, this.options);
    }, delay);
  }
  
  /**
   * Send a message through the WebSocket
   * @param {object|string} data - The data to send
   * @returns {boolean} Whether the message was sent or queued
   */
  send(data) {
    // Convert objects to JSON strings
    const message = typeof data === 'object' ? JSON.stringify(data) : data;
    
    // Check if connection is ready
    if (this.status !== ConnectionStatus.CONNECTED) {
      // Queue message for later if not connected
      if (this.options.autoReconnect && this.status !== ConnectionStatus.ERROR) {
        this.messageQueue.push(message);
        
        if (this.options.debug) {
          console.log('WebSocketService: Message queued for later delivery');
        }
        
        return true;
      }
      
      console.warn(`WebSocketService: Cannot send message - connection status is ${this.status}`);
      return false;
    }
    
    try {
      if (this.fallbackMode === 'native') {
        this.socket.send(message);
      } else if (this.fallbackMode === 'sockjs') {
        this.socket.send(message);
      }
      
      return true;
    } catch (error) {
      console.error('WebSocketService: Error sending message', error);
      
      // Queue message if auto-reconnect is enabled
      if (this.options.autoReconnect) {
        this.messageQueue.push(message);
        this.reconnect();
        return true;
      }
      
      return false;
    }
  }
  
  /**
   * Process a received WebSocket message
   * @param {MessageEvent} event - The message event
   * @private
   */
  handleMessage(event) {
    try {
      // Process different data types
      let data;
      
      if (typeof event.data === 'string') {
        try {
          // Try to parse as JSON
          data = JSON.parse(event.data);
        } catch (e) {
          // Use as-is if not valid JSON
          data = event.data;
        }
      } else if (event.data instanceof Blob) {
        // For binary data (from native WebSockets)
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const jsonStr = new TextDecoder().decode(reader.result);
            const parsed = JSON.parse(jsonStr);
            this.emit('message', parsed);
          } catch (e) {
            this.emit('message', reader.result);
          }
        };
        reader.readAsArrayBuffer(event.data);
        return;
      } else if (event.data instanceof ArrayBuffer) {
        // For ArrayBuffer data
        try {
          const jsonStr = new TextDecoder().decode(event.data);
          data = JSON.parse(jsonStr);
        } catch (e) {
          data = event.data;
        }
      } else {
        // Unknown data type, emit as-is
        data = event.data;
      }
      
      // Emit message event
      this.emit('message', data);
    } catch (error) {
      console.error('WebSocketService: Error processing message', error);
      this.emit('error', error);
    }
  }
  
  /**
   * Handle WebSocket open event
   * @private
   */
  handleOpen() {
    if (this.options.debug) {
      console.log(`WebSocketService: Connected using ${this.fallbackMode} mode`);
    }
    
    this._setStatus(ConnectionStatus.CONNECTED);
    this.reconnectCount = 0;
    this.isConnecting = false;
    
    // Set up ping interval to keep connection alive
    this._setupPing();
    
    // Send any queued messages
    this._sendQueuedMessages();
    
    // Emit the connection event
    this.emit('connect', { transportMode: this.fallbackMode });
  }
  
  /**
   * Handle WebSocket close event
   * @param {CloseEvent} event - The close event
   * @private
   */
  handleClose(event) {
    this._clearTimers();
    
    // Check if close was clean
    const wasClean = event.wasClean || (event.code === 1000);
    
    if (this.options.debug) {
      console.log(
        `WebSocketService: Connection closed${wasClean ? ' cleanly' : ''}, ` +
        `code: ${event.code}, reason: ${event.reason || 'unknown'}`
      );
    }
    
    this._setStatus(ConnectionStatus.DISCONNECTED);
    this.isConnecting = false;
    
    // Emit close event
    this.emit('close', { 
      code: event.code, 
      reason: event.reason, 
      wasClean 
    });
    
    // Attempt reconnection for unexpected closes if auto-reconnect is enabled
    if (!wasClean && this.options.autoReconnect) {
      this.reconnect();
    }
  }
  
  /**
   * Handle WebSocket error event
   * @param {Event} event - The error event
   * @private
   */
  handleError(event) {
    console.error('WebSocketService: Connection error', event);
    
    // Emit error event with more informative message
    this.emit('error', new Error(
      `WebSocket error (mode: ${this.fallbackMode}): ${event.message || 'Unknown error'}`
    ));
    
    // Don't set error status here - let close handler decide if reconnection is needed
  }
  
  /**
   * Set up ping interval to prevent timeouts and detect connection issues
   * @private
   */
  _setupPing() {
    // Clear any existing ping interval
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    
    // Set new ping interval (every 30 seconds)
    this.pingInterval = setInterval(() => {
      if (this.status === ConnectionStatus.CONNECTED) {
        this.send({ type: 'ping', timestamp: Date.now() });
      }
    }, 30000);
  }
  
  /**
   * Send any messages that were queued while disconnected
   * @private
   */
  _sendQueuedMessages() {
    if (this.messageQueue.length > 0 && this.options.debug) {
      console.log(`WebSocketService: Sending ${this.messageQueue.length} queued messages`);
    }
    
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      try {
        if (this.fallbackMode === 'native') {
          this.socket.send(message);
        } else if (this.fallbackMode === 'sockjs') {
          this.socket.send(message);
        }
      } catch (error) {
        console.error('WebSocketService: Error sending queued message', error);
        // Put the message back in the queue
        this.messageQueue.unshift(message);
        break;
      }
    }
  }
  
  /**
   * Clear all timers
   * @private
   */
  _clearTimers() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
  
  /**
   * Set connection status and emit events
   * @param {string} status - The new status
   * @private
   */
  _setStatus(status) {
    if (this.status !== status) {
      const previousStatus = this.status;
      this.status = status;
      
      // Emit status change event
      this.emit('statusChange', { 
        previous: previousStatus, 
        current: status 
      });
      
      // Emit specific events for certain status changes
      if (status === ConnectionStatus.CONNECTED) {
        this.emit('connected');
      } else if (status === ConnectionStatus.DISCONNECTED) {
        this.emit('disconnected');
      } else if (status === ConnectionStatus.RECONNECTING) {
        this.emit('reconnecting');
      } else if (status === ConnectionStatus.ERROR) {
        this.emit('connectionError');
      }
    }
  }
  
  /**
   * Get current connection status
   * @returns {string} The current connection status
   */
  getStatus() {
    return this.status;
  }
  
  /**
   * Get current fallback mode
   * @returns {string|null} The current fallback mode ('native', 'sockjs', or null if not connected)
   */
  getFallbackMode() {
    return this.fallbackMode;
  }
  
  /**
   * Check if currently connected
   * @returns {boolean} Whether the connection is active
   */
  isConnected() {
    return this.status === ConnectionStatus.CONNECTED;
  }
  
  /**
   * Get browser compatibility information
   * @returns {Object} Object containing browser compatibility information
   */
  getCompatibilityInfo() {
    return {
      hasNativeWebSocket: compatibilityCheck.hasNativeWebSocket(),
      needsFallback: compatibilityCheck.needsSockJSFallback(),
      supportsBinary: compatibilityCheck.supportsBinaryMessages(),
      supportsSubprotocols: compatibilityCheck.supportsSubprotocols(),
      maxMessageSize: compatibilityCheck.getMaxMessageSize(),
      currentFallbackMode: this.fallbackMode,
      isSecureConnection: this.url?.startsWith('wss:') || window.location.protocol === 'https:',
      usingSSL: process.env.NODE_ENV === 'production' || this.options?.forceSecure || false
    };
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;