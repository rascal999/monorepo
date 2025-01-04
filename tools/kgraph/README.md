# KGraph - Interactive Knowledge Graph Builder

KGraph is an interactive tool for building and exploring knowledge graphs. Create nodes representing concepts or terms, and explore their connections through AI-powered explanations.

## Features

- Create and manage multiple knowledge graphs
- Interactive node graph visualization
- AI-powered explanations for each node using OpenRouter API
- Click on words in explanations to create new connected nodes
- Add personal notes for each node
- Dark theme by default
- Resizable panels for customizable layout
- Local storage persistence for graphs and node data

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   cd tools/kgraph
   npm install
   ```
3. Copy the environment file and add your OpenRouter API key:
   ```bash
   cp .env.example .env
   ```
   Get your API key from [OpenRouter](https://openrouter.ai/keys) and add it to the `.env` file.

4. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Create a new graph by clicking the "New Graph" button in the left panel
2. Enter a title for your graph - this will be the first node
3. Click on a node to view its details in the right panel
4. Use the chat to get AI explanations about the concept
5. Click on any word in the AI's response to create a new connected node
6. Add personal notes in the Notes tab
7. Resize panels by dragging the dividers
8. Collapse the left panel using the chevron button for more space

## Technologies Used

- React + Vite
- TailwindCSS
- React Flow for graph visualization
- OpenRouter API for AI explanations
- React Resizable Panels for layout
- Local Storage for data persistence

## Development

The project structure follows a standard React application layout:

```
src/
  ├── components/        # React components
  │   ├── GraphPanel.jsx    # Graph visualization
  │   ├── NodePanel.jsx     # Node details and tabs
  │   └── SidebarPanel.jsx  # Graph management
  ├── App.jsx           # Main application component
  ├── main.jsx         # Application entry point
  └── index.css        # Global styles and Tailwind
```

## License

MIT
