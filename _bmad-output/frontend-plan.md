# Frontend Implementation Plan

## Overview

Add a simple, ChatGPT-like web interface that allows users to enter free text and receive structured decision analysis.

## Design Goals

1. **ChatGPT-like Experience**: Simple text input, conversation-style interface
2. **Free Text Input**: Users can describe their decision in natural language
3. **Smart Parsing**: Extract decision context and options from free text
4. **Beautiful Results**: Display structured analysis in an easy-to-read format
5. **Modern UI**: Clean, responsive design

## Technology Stack

**Option 1: Simple HTML/JS (Recommended for MVP)**
- Vanilla JavaScript
- Modern CSS (no framework needed)
- Direct API calls to backend
- Fast to implement, easy to maintain

**Option 2: React (If more complex features needed)**
- React + Vite
- Tailwind CSS for styling
- More scalable for future features

**Recommendation**: Start with Option 1 (HTML/JS) for simplicity and speed.

## Features

### Core Features
1. **Text Input Area**: Large textarea for free-form decision description
2. **Submit Button**: Send request to backend
3. **Loading State**: Show spinner while processing
4. **Results Display**: 
   - Winner recommendation (prominent)
   - Confidence score
   - Criteria breakdown
   - Option scores
   - Detected biases
   - Trade-offs and assumptions
5. **Error Handling**: Display errors in user-friendly format
6. **Request History**: Show previous requests (optional, can add later)

### UI Components
- Header with logo/title
- Main chat area
- Input area (sticky at bottom)
- Results cards/sections
- Loading indicator
- Error messages

## Implementation Plan

### Phase 1: Basic Frontend (MVP)
1. Create `frontend/` directory
2. Simple HTML page with text input
3. JavaScript to call API
4. Display results in readable format
5. Basic styling

### Phase 2: Enhanced UX
1. Better parsing of free text
2. Conversation history
3. Copy/share results
4. Better error messages

### Phase 3: Advanced Features (Future)
1. Save decisions
2. Export results
3. Comparison view
4. Dark mode

## File Structure

```
frontend/
├── index.html          # Main HTML page
├── styles.css          # Styling
├── app.js              # JavaScript logic
└── assets/             # Images, icons (if needed)
```

## API Integration

The frontend will:
1. Parse free text to extract:
   - Decision context
   - Options (if mentioned)
   - Constraints (if mentioned)
2. Call `POST /v1/decisions/analyze`
3. Display structured response

## Text Parsing Strategy

**Simple Approach (MVP)**:
- Ask user to format: "I need to decide between [Option A] and [Option B]. Context: [description]"
- Or use a simple prompt to help users structure their input

**Advanced Approach (Future)**:
- Use LLM to parse free text and extract structured data
- More natural language understanding

## Next Steps

1. Create frontend directory structure
2. Build basic HTML/CSS/JS interface
3. Integrate with existing API
4. Test with real decisions
5. Polish UI/UX

