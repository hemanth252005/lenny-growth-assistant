import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  BookOpen,
  Bot,
  ChevronDown,
  Copy,
  FileText,
  Lightbulb,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  X,
} from 'lucide-react'
import './App.css'

const API_URL = 'http://localhost:8000'

const starterQuestions = [
  'How should a startup find product-market fit?',
  'What makes a great product manager?',
  'How do successful companies prioritize?',
]

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [provider, setProvider] = useState('ollama')
  const [loading, setLoading] = useState(false)
  const [artifact, setArtifact] = useState(null)
  const [showSources, setShowSources] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    createSession()
  }, [])

  async function createSession() {
    try {
      const response = await fetch(`${API_URL}/api/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'New conversation',
          provider,
        }),
      })

      if (!response.ok) {
        throw new Error('Unable to create session')
      }

      const data = await response.json()
      setSessionId(data.id)
      setMessages([])
      setArtifact(null)
    } catch (error) {
      console.error(error)
    }
  }

  async function sendMessage(text = question) {
    const cleanQuestion = text.trim()

    if (!cleanQuestion || loading) {
      return
    }

    setQuestion('')
    setLoading(true)

    const temporaryMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: cleanQuestion,
    }

    setMessages(prev => [...prev, temporaryMessage])

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: cleanQuestion,
          provider,
          session_id: sessionId,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Chat request failed')
      }

      setMessages(prev => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          provider: data.provider || provider,
          grounded: data.grounded,
        },
      ])
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: `I couldn't complete that request. ${error.message}`,
          error: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  async function generateShip30() {
    if (!question.trim() || loading) {
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/ship30`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          provider,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ship30 generation failed')
      }

      setArtifact({
        title: 'Ship30 Essay',
        type: 'markdown',
        content: data.essay,
        sources: data.sources || [],
      })

      setQuestion('')
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  function copyArtifact() {
    if (!artifact) {
      return
    }

    navigator.clipboard.writeText(artifact.content)
    setCopied(true)

    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Sparkles size={18} />
          </div>

          <div>
            <div className="brand-title">Lenny</div>
            <div className="brand-subtitle">Growth Assistant</div>
          </div>

          <button
            className="icon-button mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        <button className="new-chat-button" onClick={createSession}>
          <Plus size={17} />
          New conversation
        </button>

        <div className="sidebar-section">
          <div className="sidebar-label">Workspace</div>

          <div className="sidebar-item active">
            <MessageSquare size={16} />
            <span>Growth conversations</span>
          </div>

          <div className="sidebar-item">
            <BookOpen size={16} />
            <span>Podcast knowledge base</span>
          </div>

          <div className="sidebar-item">
            <FileText size={16} />
            <span>Generated artifacts</span>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <div>
            <strong>Local knowledge base</strong>
            <span>14,107 indexed chunks</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button
            className="icon-button menu-button"
            onClick={() => setSidebarOpen(prev => !prev)}
          >
            <Menu size={20} />
          </button>

          <div className="mobile-title">
            <strong>Lenny Growth Assistant</strong>
          </div>

          <div className="provider-control">
            <span className="provider-label">Model</span>

            <div className="provider-select">
              <Bot size={16} />

              <select
                value={provider}
                onChange={event => setProvider(event.target.value)}
              >
                <option value="ollama">Ollama · Local</option>
                <option value="claude">Claude Agent</option>
              </select>

              <ChevronDown size={15} />
            </div>
          </div>
        </header>

        <div className="content-layout">
          <section className="chat-panel">
            {messages.length === 0 ? (
              <div className="welcome">
                <div className="welcome-icon">
                  <Sparkles size={25} />
                </div>

                <h1>Think better with Lenny's podcast.</h1>

                <p>
                  Ask product, growth, leadership, or startup questions.
                  Answers are grounded in Lenny's Podcast transcripts.
                </p>

                <div className="starter-grid">
                  {starterQuestions.map(item => (
                    <button
                      key={item}
                      className="starter-card"
                      onClick={() => sendMessage(item)}
                    >
                      <Lightbulb size={17} />
                      <span>{item}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="messages">
                {messages.map(message => (
                  <div
                    className={`message-row ${message.role}`}
                    key={message.id}
                  >
                    <div className="message-avatar">
                      {message.role === 'assistant' ? (
                        <Sparkles size={15} />
                      ) : (
                        'H'
                      )}
                    </div>

                    <div className="message-body">
                      <div className="message-name">
                        {message.role === 'assistant' ? 'Lenny' : 'You'}
                      </div>

                      <div
                        className={`message-content ${
                          message.error ? 'error-message' : ''
                        }`}
                      >
                        {message.role === 'assistant' ? (
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        ) : (
                          message.content
                        )}
                      </div>

                      {message.role === 'assistant' &&
                        message.sources?.length > 0 && (
                          <div className="sources">
                            <button
                              className="sources-header"
                              onClick={() =>
                                setShowSources(prev => !prev)
                              }
                            >
                              <BookOpen size={14} />
                              {message.sources.length} grounded source
                              {message.sources.length === 1 ? '' : 's'}
                              <ChevronDown
                                size={14}
                                className={showSources ? 'rotated' : ''}
                              />
                            </button>

                            {showSources && (
                              <div className="source-list">
                                {message.sources.map((source, index) => (
                                  <div className="source-card" key={index}>
                                    <div className="source-number">
                                      {index + 1}
                                    </div>

                                    <div>
                                      <strong>
                                        {source.episode_title}
                                      </strong>

                                      <span>
                                        {source.guest_name || 'Unknown guest'}
                                        {' · '}
                                        {source.timestamp ||
                                          source.topic ||
                                          'Transcript'}
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="message-row assistant">
                    <div className="message-avatar">
                      <Sparkles size={15} />
                    </div>

                    <div className="message-body">
                      <div className="message-name">Lenny</div>

                      <div className="typing">
                        <span />
                        <span />
                        <span />
                        <em>Searching the podcast archive…</em>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>

          {artifact && (
            <aside className="artifact-panel">
              <div className="artifact-header">
                <div>
                  <div className="artifact-kicker">Artifact</div>
                  <h2>{artifact.title}</h2>
                </div>

                <div className="artifact-actions">
                  <button
                    className="icon-button"
                    onClick={copyArtifact}
                    title="Copy artifact"
                  >
                    <Copy size={16} />
                  </button>

                  <button
                    className="icon-button"
                    onClick={() => setArtifact(null)}
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>

              {copied && <div className="copied">Copied to clipboard</div>}

              <div className="artifact-content">
                <ReactMarkdown>{artifact.content}</ReactMarkdown>
              </div>
            </aside>
          )}
        </div>

        <div className="composer-area">
          <div className="composer">
            <textarea
              value={question}
              onChange={event => setQuestion(event.target.value)}
              onKeyDown={event => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  sendMessage()
                }
              }}
              placeholder="Ask a product or growth question…"
              rows={1}
            />

            <div className="composer-actions">
              <div className="composer-hint">
                <span>Enter to send</span>
                <span>·</span>
                <span>Shift + Enter for new line</span>
              </div>

              <div className="composer-buttons">
                <button
                  className="ship30-button"
                  onClick={generateShip30}
                  disabled={!question.trim() || loading}
                >
                  <FileText size={15} />
                  Ship30
                </button>

                <button
                  className="send-button"
                  onClick={() => sendMessage()}
                  disabled={!question.trim() || loading}
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </div>

          <div className="disclaimer">
            Grounded exclusively in the indexed Lenny's Podcast transcript
            archive.
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
