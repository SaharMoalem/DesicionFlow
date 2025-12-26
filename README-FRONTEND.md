# DecisionFlow Frontend

A simple, ChatGPT-like web interface for DecisionFlow.

## Quick Start

1. **Make sure the backend is running:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Open the frontend:**
   - The frontend is served automatically at: http://localhost:8000/
   - Or open `frontend/index.html` directly in your browser

3. **Use it:**
   - Enter your decision in natural language
   - Click "Analyze Decision" or press Ctrl+Enter
   - View the structured analysis results

## Features

- ✅ ChatGPT-like text input
- ✅ Natural language decision parsing
- ✅ Beautiful result display
- ✅ Responsive design
- ✅ Error handling

## Example Inputs

**Simple:**
```
Should we choose AWS or GCP for our new microservice? We need high scalability and low cost, with a budget of $50,000.
```

**Detailed:**
```
I need to decide between hiring a senior engineer now or waiting 3 months. We have budget of $150,000 but need to balance immediate needs vs long-term planning. Timeline is Q1.
```

**With Constraints:**
```
Should we build feature X now or postpone it? Budget: $100,000. Timeline: 3 months. We need to consider user value and technical complexity.
```

## How It Works

1. **Text Parsing**: The frontend extracts:
   - Decision context (the problem description)
   - Options (from patterns like "between X and Y", "X or Y")
   - Constraints (budget, timeline, etc.)

2. **API Call**: Sends structured request to `/v1/decisions/analyze`

3. **Result Display**: Shows:
   - Winner recommendation
   - Confidence score
   - Evaluation criteria
   - Option scores
   - Detected biases
   - Trade-offs and assumptions

## Development

The frontend is simple HTML/CSS/JavaScript - no build step required!

- `index.html` - Main page structure
- `styles.css` - Styling
- `app.js` - Application logic

## Future Enhancements

- Better natural language parsing (using LLM)
- Conversation history
- Save/share decisions
- Export results
- Dark mode

