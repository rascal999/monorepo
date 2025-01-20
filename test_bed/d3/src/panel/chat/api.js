import { wrapWordsInClickableSpans } from './utils.js';

const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;
const OPENROUTER_MODEL = import.meta.env.VITE_OPENROUTER_MODEL;

export async function streamOpenRouterResponse(messages) {
  try {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': window.location.origin,
      },
      body: JSON.stringify({
        model: OPENROUTER_MODEL,
        messages: messages,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let responseText = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;
          
          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices[0]?.delta?.content;
            if (content) {
              responseText += content;
              // Update UI with streamed content
              const tempMsg = document.querySelector('.chat-message.streaming');
              if (tempMsg) {
                tempMsg.innerHTML = wrapWordsInClickableSpans(responseText);
              }
            }
          } catch (e) {
            console.error('Error parsing SSE message:', e);
          }
        }
      }
    }

    return responseText;
  } catch (error) {
    console.error('Error calling OpenRouter API:', error);
    throw error;
  }
}
