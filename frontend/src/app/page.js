
"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { CHAT_API_URL } from "./constants";
import { useAuth } from "./contexts/AuthContext";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, isLoading: authLoading, logout, getAuthHeaders } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Show loading screen while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#131314] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!user) {
    return null;
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    const userMessage = { sender: "user", text: trimmedInput };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      
      setMessages((prevMessages) => [...prevMessages, { sender: "bot", text: "", isLoading: true }]);

      const response = await axios.post(CHAT_API_URL, {
        query: trimmedInput,
      }, {
        headers: getAuthHeaders(),
      });

      
      setMessages((prevMessages) => [
        ...prevMessages.filter(msg => !msg.isLoading),
        { 
          sender: "bot", 
          text: response.data.answer,
          trace: response.data.trace || null
        }
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
     
      setMessages((prevMessages) => [
        ...prevMessages.filter(msg => !msg.isLoading),
        { sender: "bot", text: "The question appears to be outside the scope of the MeTTa documentation; please ask me about MeTTa." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const formatBotResponse = (text) => {
    const paragraphs = text.split("\n").filter((line) => line.trim() !== "");
    return paragraphs.map((paragraph, index) => {
      if (paragraph.trim().startsWith("- ") || paragraph.trim().startsWith("• ")) {
        const items = paragraph.split("\n").filter((item) => item.trim() !== "");
        return (
          <ul key={index} className="list-disc list-inside space-y-1">
            {items.map((item, i) => (
              <li key={i} className="text-gray-200">
                {item.replace(/^- |^• /, "")}
              </li>
            ))}
          </ul>
        );
      }
      return (
        <p key={index} className="text-gray-200 mb-2">
          {paragraph}
        </p>
      );
    });
  };

  const renderTrace = (trace, messageIndex) => {
    if (!trace || !trace.stages) return null;

    // Stage mapping for display
    const stageMap = {
      'retrieval': { title: '1. Document & Tool Retrieval', icon: '🔍', color: 'text-indigo-400' },
      'isrel': { title: '2. Relevance Check', icon: '✅', color: 'text-green-400' },
      'generation': { title: '3. Initial Answer Generation', icon: '💡', color: 'text-yellow-400' },
      'issup': { title: '4. Factuality Check (Support)', icon: '🛡️', color: 'text-red-400' },
      'isuse': { title: '5. Usefulness & Critique', icon: '✨', color: 'text-purple-400' },
      'retrieval_after_rewrite': { title: '2b. Re-retrieval After Rewrite', icon: '🔄', color: 'text-blue-400' },
      'isrel_after_rewrite': { title: '2c. Relevance Re-check', icon: '🔍', color: 'text-green-400' },
      'refinement': { title: '6. Answer Refinement', icon: '🔧', color: 'text-orange-400' },
      're_retrieval': { title: '7. Guided Re-retrieval', icon: '🎯', color: 'text-cyan-400' },
      'abort': { title: '⚠ Process Aborted', icon: '⛔', color: 'text-red-400' },
      'stop': { title: '🛑 Process Stopped', icon: '⏹️', color: 'text-gray-400' }
    };

    const renderStageContent = (stageData) => {
      let content = '';
      
      // Handle Retrieval Stage
      if (stageData.stage === 'retrieval' || stageData.stage === 'retrieval_after_rewrite' || stageData.stage === 're_retrieval') {
        const ids = stageData.retrieved_ids || stageData.new_ids || [];
        content += `<h4 class="font-semibold text-gray-300 mb-2">Retrieved Document IDs:</h4>`;
        content += `<ul class="list-disc list-inside space-y-1 ml-4 text-sm text-gray-400">`;
        ids.forEach(id => {
          content += `<li class="truncate">${id}</li>`;
        });
        content += `</ul>`;
        if (stageData.note) {
          content += `<p class="mt-2 text-xs text-gray-500 italic">${stageData.note}</p>`;
        }
      } 
      // Handle Relevance Check Stage
      else if (stageData.stage === 'isrel' || stageData.stage === 'isrel_after_rewrite') {
        const result = stageData.result;
        content += `<p class="text-sm"><strong>Relevance:</strong> <span class="font-bold ${result.is_relevant ? 'text-green-400' : 'text-red-400'}">${result.is_relevant ? 'Relevant' : 'Not Relevant'}</span></p>`;
        content += `<p class="text-sm"><strong>Relevance Score:</strong> ${result.relevance_score?.toFixed(2) || 'N/A'}</p>`;
        content += `<p class="mt-2 text-sm"><strong>Reason:</strong> ${result.reason}</p>`;
      } 
      // Handle Generation Stage
      else if (stageData.stage === 'generation') {
        content += `<h4 class="font-semibold text-gray-300 mb-2">Generated Draft:</h4>`;
        content += `<p class="text-sm italic p-3 bg-gray-800 rounded-md border border-gray-600">${stageData.answer}</p>`;
      } 
      // Handle Factuality Check (issup) Stage
      else if (stageData.stage === 'issup') {
        const result = stageData.result;
        content += `<p class="text-sm"><strong>Fully Supported:</strong> <span class="font-bold ${result.fully_supported ? 'text-green-400' : 'text-red-400'}">${result.fully_supported ? 'Yes' : 'No'}</span></p>`;
        content += `<p class="mt-2 text-sm"><strong>Review Comment:</strong> ${result.comment}</p>`;
        if (result.contradictions && result.contradictions.length > 0) {
          content += `<p class="mt-2 text-sm text-red-400"><strong>Contradictions Found:</strong> ${result.contradictions.join(', ')}</p>`;
        }
        if (result.unsupported_claims && result.unsupported_claims.length > 0) {
          content += `<p class="mt-2 text-sm text-yellow-400"><strong>Unsupported Claims:</strong> ${result.unsupported_claims.join(', ')}</p>`;
        }
        if (result.missing_items && result.missing_items.length > 0) {
          content += `<p class="mt-2 text-sm text-blue-400"><strong>Missing Items:</strong> ${result.missing_items.join(', ')}</p>`;
        }
      } 
      // Handle Usefulness Check (isuse) Stage
      else if (stageData.stage === 'isuse') {
        const result = stageData.result;
        content += `<p class="text-sm"><strong>Usefulness Score:</strong> ${result.score?.toFixed(2) || 'N/A'}</p>`;
        content += `<p class="text-sm"><strong>Result:</strong> <span class="font-bold ${result.useful ? 'text-green-400' : 'text-red-400'}">${result.useful ? 'Useful' : 'Not Useful'}</span></p>`;
        content += `<p class="mt-2 text-sm"><strong>Critique:</strong> ${result.comment}</p>`;
      }
      // Handle Refinement Stage
      else if (stageData.stage === 'refinement') {
        content += `<h4 class="font-semibold text-gray-300 mb-2">Refined Answer:</h4>`;
        content += `<p class="text-sm italic p-3 bg-gray-800 rounded-md border border-gray-600">${stageData.new_answer}</p>`;
        if (stageData.rounds) {
          content += `<p class="mt-2 text-xs text-gray-500">Refinement Round: ${stageData.rounds}</p>`;
        }
      }
      // Handle Abort/Stop Stages
      else if (stageData.stage === 'abort' || stageData.stage === 'stop') {
        content += `<p class="text-sm text-red-400"><strong>Reason:</strong> ${stageData.reason || 'Process terminated'}</p>`;
        if (stageData.rounds) {
          content += `<p class="mt-2 text-xs text-gray-500">Stopped after ${stageData.rounds} rounds</p>`;
        }
      }

      return content;
    };

    return (
      <div className="mt-4 pt-4 border-t border-gray-700">
        {/* Quality Status */}
        {trace.passed !== undefined && (
          <div className="mb-4 flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              trace.passed ? 'bg-green-900 text-green-300 border border-green-700' : 'bg-red-900 text-red-300 border border-red-700'
            }`}>
              {trace.passed ? '✓ Quality Check Passed' : '⚠ Quality Check Failed'}
            </span>
            <span className="text-xs text-gray-500">
              {trace.stages.length} reasoning steps
            </span>
          </div>
        )}

        {/* Collapsible Trace Section */}
        <div className="border border-gray-600 rounded-lg overflow-hidden">
          <button 
            onClick={() => {
              const container = document.getElementById(`trace-container-${messageIndex}`);
              const icon = document.getElementById(`toggle-icon-${messageIndex}`);
              if (container && icon) {
                container.classList.toggle('hidden');
                icon.classList.toggle('rotate-180');
              }
            }}
            className="w-full flex justify-between items-center p-4 text-left font-semibold text-sm text-gray-300 hover:bg-gray-800 transition duration-150 focus:outline-none"
          >
            <span className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 text-blue-400">
                <rect width="18" height="18" x="3" y="3" rx="2"></rect>
                <path d="m10 14-2-2 2-2"></path>
                <path d="m14 10 2 2-2 2"></path>
              </svg>
              View Chain of Thought Trace
            </span>
            <svg id={`toggle-icon-${messageIndex}`} className="w-4 h-4 transform transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <div id={`trace-container-${messageIndex}`} className="hidden p-4 bg-gray-800 border-t border-gray-600">
            <div className="space-y-4 max-h-96 overflow-y-auto trace-scroll">
              {trace.stages.map((stageData, index) => {
                const map = stageMap[stageData.stage] || { title: stageData.stage, icon: '⚙️', color: 'text-gray-400' };
                
                return (
                  <div key={index} className="p-4 bg-gray-900 rounded-lg border-l-4 border-gray-600">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`${map.color} text-lg`}>{map.icon}</span>
                      <h3 className="font-bold text-gray-200">{map.title}</h3>
                      {stageData.round && (
                        <span className="text-xs text-gray-500 bg-gray-700 px-2 py-1 rounded">
                          Round {stageData.round}
                        </span>
                      )}
                    </div>
                    <div 
                      className="text-gray-300"
                      dangerouslySetInnerHTML={{ __html: renderStageContent(stageData) }}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-[#131314] overflow-hidden">
      {/* Sidebar */}
      <div
        className={`bg-[#1f1f1f] text-gray-300 flex flex-col transition-all duration-300 ease-in-out ${
          isSidebarOpen ? "w-64" : "w-16"
        }`}
      >
        <div className="p-4 flex justify-center items-center border-b border-gray-700">
          <button
            onClick={toggleSidebar}
            className="text-gray-400 hover:text-white focus:outline-none"
            aria-label={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        <div className={`flex-grow p-4 overflow-y-auto ${!isSidebarOpen && "hidden"}`}>
          {/* User Info */}
          {user && (
            <div className="mb-6 p-3 bg-gray-800 rounded-lg border border-gray-600">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-violet-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-200">{user.username}</p>
                  <p className="text-xs text-gray-400">{user.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="w-full mt-2 px-3 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded transition duration-200"
              >
                Sign Out
              </button>
            </div>
          )}
          
          <h2 className="text-lg font-semibold mb-4">Chat History</h2>
          <ul>
            <li className="py-1 px-2 rounded hover:bg-gray-700 cursor-pointer text-sm truncate">
              Chat 1
            </li>
            <li className="py-1 px-2 rounded hover:bg-gray-700 cursor-pointer text-sm truncate">
              Previous discussion
            </li>
            <li className="py-1 px-2 rounded hover:bg-gray-700 cursor-pointer text-sm truncate">
              Old chat title here
            </li>
          </ul>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-grow overflow-y-auto px-6 md:px-20 lg:px-32 py-6 space-y-8 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
            {messages.length === 0 ? (
              <div className="flex justify-center items-center h-full">
                <h1 className="text-5xl font-medium text-gray-400 bg-gradient-to-r from-cyan-400 via-violet-500 to-lime-400 bg-clip-text text-transparent">
                  Welcome to MeTTa Standard Library chatbot!
                </h1>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className="flex flex-col">
                  {/* User's Message */}
                  {msg.sender === "user" && (
                    <div className="flex justify-end mb-4">
                      <div
                        className="px-5 py-3 rounded-xl shadow-lg text-white"
                        style={{
                          background: "linear-gradient(145deg, #2e2e2e, #1f1f1f)",
                          border: "1px solid #3a3a3a",
                          maxWidth: "90%",
                        }}
                      >
                        <span className="text-base">{msg.text}</span>
                      </div>
                    </div>
                  )}

                  {/* Bot's Response */}
                  {msg.sender === "bot" && (
                    <div className="flex justify-start mb-6">
                      <div className="px-6 py-5 rounded-xl w-full max-w-4xl mx-auto bg-[#1a1a1a] dark:bg-[#121212] text-gray-200 leading-relaxed shadow-md border border-gray-700">
                        {msg.isLoading ? (
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"></div>
                            <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-75"></div>
                            <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-150"></div>
                          </div>
                        ) : (
                          <>
                            <div className="text-xl mb-3">✨</div>
                            <div className="whitespace-pre-wrap break-words text-[17px] font-normal">
                              {formatBotResponse(msg.text)}
                            </div>
                            {renderTrace(msg.trace, index)}
                          </>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="pb-4 pt-2 px-4 sm:px-6 lg:px-8">
            <div className="flex justify-center">
              <div className="flex items-center bg-[#1f1f1f] p-2 rounded-full shadow-md border border-gray-700 w-full md:w-3/4 lg:w-1/2">
                <button className="p-2 text-gray-400 hover:text-gray-200 focus:outline-none flex-shrink-0">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about MeTTa Standard Library..."
                  className="flex-grow px-4 py-3 mx-2 bg-transparent text-gray-300 focus:outline-none min-h-[50px]"
                  disabled={isLoading}
                />

                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  className={`p-2 rounded-full text-gray-400 flex-shrink-0 ${
                    input.trim() && !isLoading ? "hover:bg-gray-600 hover:text-gray-200" : "opacity-50 cursor-not-allowed"
                  } focus:outline-none`}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M10.894 2.553a1 1 0 00-1.789 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 16.11V3.89a1 1 0 00.894-.337l2-2a1 1 0 00-1.414-1.414l-1.47 1.47z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}