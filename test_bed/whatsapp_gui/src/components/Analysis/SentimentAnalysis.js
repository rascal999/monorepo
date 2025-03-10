import React from 'react';
import styled from 'styled-components';

/**
 * Component for displaying sentiment analysis results
 */
const SentimentAnalysis = ({ data }) => {
  // If no data is available yet
  if (!data || !data.sentiment) {
    return (
      <EmptyContainer>
        <EmptyMessage>
          No sentiment analysis available. Send more messages to analyze.
        </EmptyMessage>
      </EmptyContainer>
    );
  }
  
  // Get sentiment color
  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'var(--color-success)';
      case 'negative':
        return 'var(--color-error)';
      case 'neutral':
        return 'var(--color-text-secondary)';
      case 'mixed':
        return 'var(--color-warning)';
      default:
        return 'var(--color-text-secondary)';
    }
  };
  
  // Get emoji for sentiment
  const getSentimentEmoji = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      case 'neutral':
        return '😐';
      case 'mixed':
        return '😕';
      default:
        return '❓';
    }
  };
  
  // Format score as percentage
  const formatScore = (score) => {
    if (typeof score !== 'number') return '50%';
    return `${Math.round(score * 10)}%`;
  };
  
  return (
    <SentimentContainer>
      <SentimentHeader>
        <SentimentEmoji>
          {getSentimentEmoji(data.sentiment)}
        </SentimentEmoji>
        
        <SentimentTitle>
          Overall Sentiment: 
          <SentimentValue color={getSentimentColor(data.sentiment)}>
            {data.sentiment}
          </SentimentValue>
        </SentimentTitle>
      </SentimentHeader>
      
      <ScoreContainer>
        <ScoreLabel>Positivity Score</ScoreLabel>
        <ScoreBar>
          <ScoreFill 
            width={formatScore(data.score)} 
            color={getSentimentColor(data.sentiment)}
          />
        </ScoreBar>
        <ScoreValue>{formatScore(data.score)}</ScoreValue>
      </ScoreContainer>
      
      {data.emotions && data.emotions.length > 0 && (
        <Section>
          <SectionTitle>Detected Emotions</SectionTitle>
          <EmotionTags>
            {data.emotions.map((emotion, index) => (
              <EmotionTag key={index}>
                {emotion}
              </EmotionTag>
            ))}
          </EmotionTags>
        </Section>
      )}
      
      {data.summary && (
        <Section>
          <SectionTitle>Summary</SectionTitle>
          <SummaryText>{data.summary}</SummaryText>
        </Section>
      )}
    </SentimentContainer>
  );
};

// Styled components
const SentimentContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const SentimentHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const SentimentEmoji = styled.div`
  font-size: 2rem;
  margin-right: var(--spacing-md);
`;

const SentimentTitle = styled.h3`
  font-size: var(--font-size-md);
  margin: 0;
  display: flex;
  flex-direction: column;
`;

const SentimentValue = styled.span`
  color: ${props => props.color};
  font-weight: bold;
  margin-top: var(--spacing-xs);
`;

const ScoreContainer = styled.div`
  margin-bottom: var(--spacing-lg);
`;

const ScoreLabel = styled.div`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
`;

const ScoreBar = styled.div`
  height: 8px;
  background-color: var(--color-surface-variant);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
`;

const ScoreFill = styled.div`
  height: 100%;
  width: ${props => props.width};
  background-color: ${props => props.color};
  border-radius: 4px;
`;

const ScoreValue = styled.div`
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: right;
`;

const Section = styled.div`
  margin-bottom: var(--spacing-lg);
`;

const SectionTitle = styled.h4`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm) 0;
`;

const EmotionTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
`;

const EmotionTag = styled.div`
  background-color: var(--color-surface-variant);
  color: var(--color-text-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
`;

const SummaryText = styled.p`
  font-size: var(--font-size-sm);
  line-height: 1.5;
  margin: 0;
`;

const EmptyContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
`;

const EmptyMessage = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  text-align: center;
`;

export default SentimentAnalysis;