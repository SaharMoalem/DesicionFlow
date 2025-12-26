// DecisionFlow Frontend Application

const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const decisionInput = document.getElementById('decision-input');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const messagesContainer = document.getElementById('messages');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    submitBtn.addEventListener('click', handleSubmit);
    decisionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleSubmit();
        }
    });
});

// Parse free text to extract decision structure
function parseDecisionText(text) {
    // Simple parsing - extract options and context
    // This is a basic implementation; could be enhanced with LLM parsing
    
    const options = [];
    const constraints = {};
    let decisionContext = text;
    
    // Strategy: Split on " or " - this is the most reliable approach
    // Find " or " and extract what's before and after it
    
    // Simple and direct: find " or " and split (case insensitive)
    // Use regex to find " or " with any case
    const orMatch = text.match(/\s+[Oo]r\s+/);
    
    if (orMatch) {
        const orIndex = orMatch.index;
        const orLength = orMatch[0].length;
        
        // Get text before " or "
        const beforeOr = text.substring(0, orIndex).trim();
        // Get text after " or "
        const afterOr = text.substring(orIndex + orLength).trim();
        
        // Extract first option - remove question intro
        let opt1 = beforeOr;
        
        // Remove "Should we choose" and similar patterns
        if (opt1.toLowerCase().startsWith('should we choose ')) {
            opt1 = opt1.substring('should we choose '.length);
        } else if (opt1.toLowerCase().startsWith('should we ')) {
            // Find the first space after "should we " and remove up to the next space (the verb)
            const afterShouldWe = opt1.substring('should we '.length);
            const verbEnd = afterShouldWe.indexOf(' ');
            if (verbEnd > 0) {
                opt1 = afterShouldWe.substring(verbEnd + 1);
            } else {
                opt1 = afterShouldWe;
            }
        } else if (opt1.toLowerCase().startsWith('should i ')) {
            const afterShouldI = opt1.substring('should i '.length);
            const verbEnd = afterShouldI.indexOf(' ');
            if (verbEnd > 0) {
                opt1 = afterShouldI.substring(verbEnd + 1);
            } else {
                opt1 = afterShouldI;
            }
        }
        
        opt1 = opt1.trim();
        
        // Extract second option - stop at question mark, period, or new sentence
        let opt2 = afterOr;
        
        // Stop at first ?, !, or .
        const punctIndex = opt2.search(/[?.!]/);
        if (punctIndex > 0) {
            opt2 = opt2.substring(0, punctIndex);
        }
        
        // Also stop if we hit " We " or " Our " (start of new sentence)
        const sentenceIndex = opt2.search(/\s+(We|Our|I|The|This)\s/);
        if (sentenceIndex > 0) {
            opt2 = opt2.substring(0, sentenceIndex);
        }
        
        opt2 = opt2.trim();
        
        // Final validation
        if (opt1.length >= 3 && opt2.length >= 3) {
            options.push(opt1);
            options.push(opt2);
        } else {
            // Debug: log what we extracted
            console.log('Parser debug - extracted options:', { opt1, opt2, opt1Length: opt1.length, opt2Length: opt2.length });
        }
    } else {
        // Debug: log if we didn't find " or "
        console.log('Parser debug - no " or " found in text:', text.substring(0, 100));
    }
    
    // Pattern 2: "between X and Y"
    if (options.length === 0) {
        const betweenPattern = /between\s+(.+?)\s+and\s+(.+?)(?:\?|\.|$)/i;
        match = text.match(betweenPattern);
        if (match) {
            options.push(match[1].trim().replace(/[?.!]+$/, ''));
            options.push(match[2].trim().replace(/[?.!]+$/, ''));
        }
    }
    
    // Pattern 3: "X vs Y" or "X versus Y"
    if (options.length === 0) {
        const vsPattern = /(.+?)\s+(?:vs|versus)\s+(.+?)(?:\?|\.|$)/i;
        match = text.match(vsPattern);
        if (match) {
            options.push(match[1].trim().replace(/[?.!]+$/, ''));
            options.push(match[2].trim().replace(/[?.!]+$/, ''));
        }
    }
    
    // Pattern 4: Generic "choose/select X or Y"
    if (options.length === 0) {
        const choosePattern = /(?:choose|select|pick|decide)\s+(?:between\s+)?(.+?)\s+or\s+(.+?)(?:\?|\.|$)/i;
        match = text.match(choosePattern);
        if (match) {
            options.push(match[1].trim().replace(/[?.!]+$/, ''));
            options.push(match[2].trim().replace(/[?.!]+$/, ''));
        }
    }
    
    // Extract budget constraint
    const budgetMatch = text.match(/(?:budget|cost|spend|spending)\s+(?:of|is|:)?\s*\$?([\d,]+)/i);
    if (budgetMatch) {
        constraints.budget = parseInt(budgetMatch[1].replace(/,/g, ''));
    }
    
    // Extract timeline constraint
    const timelineMatch = text.match(/(?:timeline|deadline|time|by)\s+(?:is|:)?\s*([^,.!?]+)/i);
    if (timelineMatch && !timelineMatch[1].includes('or')) {
        constraints.timeline = timelineMatch[1].trim();
    }
    
    // If no options found, try to extract from list format
    if (options.length === 0) {
        const listMatch = text.match(/(?:options?|choices?|alternatives?):?\s*([^.!?]+)/i);
        if (listMatch) {
            const listText = listMatch[1];
            const items = listText.split(/[,;]|\s+or\s+/i).map(s => s.trim()).filter(s => s.length > 0);
            if (items.length >= 2) {
                options.push(...items.slice(0, 2)); // Take first 2
            }
        }
    }
    
    // If still no options, prompt user
    if (options.length < 2) {
        // Debug: log what we found
        console.log('Parse debug:', {
            text: text.substring(0, 100),
            foundOr: text.includes(' or ') || text.includes(' Or '),
            optionsFound: options.length,
            options: options
        });
        
        return {
            error: "I couldn't identify two clear options in your decision. Please format it like: 'Should we choose Option A or Option B? Context: [your description]'"
        };
    }
    
    return {
        decision_context: decisionContext,
        options: options.slice(0, 2), // Limit to 2 options for MVP
        constraints: Object.keys(constraints).length > 0 ? constraints : undefined
    };
}

// Handle form submission
async function handleSubmit() {
    const text = decisionInput.value.trim();
    
    if (!text) {
        showError('Please enter a decision to analyze.');
        return;
    }
    
    // Add user message to chat
    addMessage('user', text);
    
    // Clear input
    decisionInput.value = '';
    
    // Show loading
    setLoading(true);
    
    try {
        // Parse the text
        const parsed = parseDecisionText(text);
        
        if (parsed.error) {
            showError(parsed.error);
            setLoading(false);
            return;
        }
        
        // Call API
        const response = await fetch(`${API_BASE_URL}/v1/decisions/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(parsed)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Failed to analyze decision');
        }
        
        const result = await response.json();
        
        // Display result
        displayResult(result);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Add message to chat
function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'user') {
        messageDiv.textContent = content;
    } else {
        messageDiv.innerHTML = content;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Display analysis result
function displayResult(result) {
    const html = `
        <div class="result-card">
            <div class="result-header">
                <div>
                    <div class="winner">🏆 Winner: ${escapeHtml(result.winner)}</div>
                </div>
                <div class="confidence confidence-${getConfidenceClass(result.confidence)}">
                    ${(result.confidence * 100).toFixed(0)}% Confidence
                </div>
            </div>
            
            ${result.criteria.length > 0 ? `
                <div class="section">
                    <div class="section-title">📊 Evaluation Criteria</div>
                    <ul class="criteria-list">
                        ${result.criteria.map(c => `
                            <li class="criteria-item">
                                <div class="criterion-name">${escapeHtml(c.name)}</div>
                                <div class="criterion-weight">Weight: ${(c.weight * 100).toFixed(0)}%</div>
                                <div>${escapeHtml(c.rationale)}</div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${Object.keys(result.scores).length > 0 ? `
                <div class="section">
                    <div class="section-title">📈 Option Scores</div>
                    <ul class="options-list">
                        ${Object.entries(result.scores).map(([option, scores]) => `
                            <li class="option-item">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <strong>${escapeHtml(option)}</strong>
                                    <span>${(scores.total_score * 100).toFixed(0)}%</span>
                                </div>
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${scores.total_score * 100}%"></div>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${result.biases_detected.length > 0 ? `
                <div class="section">
                    <div class="section-title">⚠️ Detected Biases</div>
                    ${result.biases_detected.map(bias => `
                        <div class="bias-item">
                            <div class="bias-type">${escapeHtml(bias.bias_type)}</div>
                            <div style="margin-top: 0.5rem;">${escapeHtml(bias.description)}</div>
                            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">
                                Evidence: ${escapeHtml(bias.evidence)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${result.trade_offs && result.trade_offs.length > 0 ? `
                <div class="section">
                    <div class="section-title">⚖️ Trade-offs</div>
                    <ul>
                        ${result.trade_offs.map(to => {
                            // Handle both object format {description: "..."} and string format
                            let description;
                            if (typeof to === 'string') {
                                description = to;
                            } else if (to && typeof to === 'object') {
                                // Try multiple possible property names
                                description = to.description || to.text || to.message || to.content || JSON.stringify(to);
                            } else {
                                description = String(to);
                            }
                            return `<li class="tradeoff-item">${escapeHtml(description)}</li>`;
                        }).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${result.assumptions && result.assumptions.length > 0 ? `
                <div class="section">
                    <div class="section-title">💭 Assumptions</div>
                    <ul>
                        ${result.assumptions.map(a => `<li class="assumption-item">${escapeHtml(a)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${result.risks && result.risks.length > 0 ? `
                <div class="section">
                    <div class="section-title">⚠️ Risks</div>
                    <ul>
                        ${result.risks.map(risk => {
                            // Handle both object format and string format
                            const description = typeof risk === 'string' ? risk : (risk.description || JSON.stringify(risk));
                            return `<li class="risk-item">${escapeHtml(description)}</li>`;
                        }).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${result.what_would_change_decision && result.what_would_change_decision.length > 0 ? `
                <div class="section">
                    <div class="section-title">🔄 What Would Change the Decision</div>
                    <ul>
                        ${result.what_would_change_decision.map(factor => `<li class="factor-item">${escapeHtml(factor)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
    
    addMessage('assistant', html);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    messagesContainer.appendChild(errorDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Set loading state
function setLoading(loading) {
    submitBtn.disabled = loading;
    if (loading) {
        btnText.classList.add('hidden');
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.classList.remove('hidden');
        btnSpinner.classList.add('hidden');
    }
}

// Get confidence class for styling
function getConfidenceClass(confidence) {
    if (confidence >= 0.7) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

