import { useState, useRef, useEffect } from "react";
import {
  Send,
  Image as ImageIcon,
  Upload,
  Loader2,
  Sparkles,
  Trash2,
  Plus,
  Cpu,
  ShieldCheck,
  Search
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, loading]);

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    setImages(prev => [...prev, ...files]);

    const newPreviews = files.map(file => URL.createObjectURL(file));
    setPreviews(prev => [...prev, ...newPreviews]);
  };

  const removeImage = (index) => {
    setImages(images.filter((_, i) => i !== index));
    setPreviews(previews.filter((_, i) => i !== index));
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    const currentQuestion = question;
    const currentImages = [...images];

    setQuestion("");
    setLoading(true);

    // Add user message to chat history
    setChatHistory(prev => [...prev, {
      type: 'user',
      content: currentQuestion,
      images: previews // Store previews for the history display
    }]);

    const formData = new FormData();
    formData.append("question", currentQuestion);
    currentImages.forEach((img) => formData.append("images", img));

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setChatHistory(prev => [...prev, {
        type: 'ai',
        content: data.answer,
        status: 'success'
      }]);
    } catch (err) {
      setChatHistory(prev => [...prev, {
        type: 'ai',
        content: "I encountered an error connecting to the vision engine. Please ensure the backend is running and try again.",
        status: 'error'
      }]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app-container fade-in">
      {/* Sidebar: Image Management */}
      <aside className="sidebar">
        <div className="glass header" style={{ padding: '1rem', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="app-title">
            <Sparkles size={24} className="text-indigo-400" />
            <span>VisionAI </span>
          </div>
          <button
            onClick={() => {
              setImages([]);
              setPreviews([]);
              setChatHistory([]);
              setQuestion("");
            }}
            className="send-btn"
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              color: '#ef4444',
              padding: '6px 12px',
              fontSize: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              border: '1px solid rgba(239, 68, 68, 0.2)'
            }}
            title="Clear all data and exit session"
          >
            <Trash2 size={14} />
            Reset
          </button>
        </div>

        <div className="glass stats-panel">
          <div className="stat-item">
            <span className="stat-label">Model</span>
            <span className="stat-value">Gemini-V</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">System</span>
            <span className="stat-value">Active</span>
          </div>
        </div>

        <div className="glass image-gallery" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Reference Images</h3>
            <button
              onClick={() => fileInputRef.current.click()}
              className="send-btn"
              style={{ width: '32px', height: '32px', padding: 0, borderRadius: '8px' }}
            >
              <Plus size={18} />
            </button>
          </div>

          <input
            type="file"
            multiple
            hidden
            ref={fileInputRef}
            onChange={handleImageUpload}
            accept="image/*"
          />

          {previews.length === 0 ? (
            <div style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-secondary)',
              gap: '0.5rem',
              border: '2px dashed var(--glass-border)',
              borderRadius: '12px'
            }}>
              <ImageIcon size={32} opacity={0.3} />
              <p style={{ fontSize: '0.8rem' }}>No images uploaded</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <AnimatePresence>
                {previews.map((src, idx) => (
                  <motion.div
                    key={src}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="image-card"
                  >
                    <img src={src} alt={`Upload ${idx}`} />
                    <span className="image-badge badge-valid">
                      <ShieldCheck size={10} style={{ marginRight: '2px' }} />
                      Verified
                    </span>
                    <button
                      onClick={() => removeImage(idx)}
                      style={{
                        position: 'absolute',
                        bottom: '8px',
                        right: '8px',
                        background: 'rgba(239, 68, 68, 0.8)',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '4px',
                        color: 'white',
                        cursor: 'pointer'
                      }}
                    >
                      <Trash2 size={12} />
                    </button>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content: Chat Interface */}
      <main className="main-content">
        <div className="glass chat-container">
          <div className="chat-messages">
            {chatHistory.length === 0 && !loading && (
              <div style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                gap: '1rem',
                opacity: 0.7
              }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  background: 'var(--bg-accent)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 30px var(--accent-glow)'
                }}>
                  <Cpu size={32} className="text-indigo-400" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>How can I help you today?</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Upload images and ask questions about them. <br />
                    I can detect objects, read text, or describe scenes.
                  </p>
                </div>
              </div>
            )}

            {chatHistory.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`message ${msg.type === 'user' ? 'message-user' : 'message-ai'}`}
              >
                {msg.type === 'user' && msg.images && msg.images.length > 0 && (
                  <div style={{ display: 'flex', gap: '4px', marginBottom: '8px', flexWrap: 'wrap' }}>
                    {msg.images.map((img, i) => (
                      <img key={i} src={img} alt="Query ref" style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover', border: '1px solid rgba(255,255,255,0.2)' }} />
                    ))}
                  </div>
                )}
                {msg.content}
                {msg.status === 'error' && (
                  <div style={{ fontSize: '0.7rem', color: '#ffbaba', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    Critical Error Occurred
                  </div>
                )}
              </motion.div>
            ))}

            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="message message-ai"
              >
                <div className="typing-dots">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </motion.div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-area">
            <button
              onClick={() => fileInputRef.current.click()}
              className="send-btn"
              style={{ background: 'var(--bg-accent)', color: 'var(--text-secondary)' }}
              title="Upload Image"
            >
              <Upload size={20} />
            </button>
            <input
              type="text"
              className="chat-input"
              placeholder={images.length > 0 ? "Ask about selected images..." : "Upload images or ask a question..."}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button
              onClick={askQuestion}
              className="send-btn"
              disabled={loading || !question.trim()}
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
