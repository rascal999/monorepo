import React from 'react';
import styled from 'styled-components';

/**
 * Component for displaying relationship analysis results
 */
const RelationshipAnalysis = ({ data }) => {
  // If no data is available yet
  if (!data || !data.quality) {
    return (
      <EmptyContainer>
        <EmptyMessage>
          No relationship analysis available. Send more messages to analyze.
        </EmptyMessage>
      </EmptyContainer>
    );
  }
  
  // Get quality color
  const getQualityColor = (quality) => {
    switch (quality.toLowerCase()) {
      case 'excellent':
      case 'good':
        return 'var(--color-success)';
      case 'poor':
      case 'bad':
        return 'var(--color-error)';
      case 'fair':
      case 'average':
        return 'var(--color-warning)';
      default:
        return 'var(--color-text-secondary)';
    }
  };
  
  // Get communication color
  const getCommunicationColor = (communication) => {
    switch (communication.toLowerCase()) {
      case 'excellent':
      case 'good':
        return 'var(--color-success)';
      case 'poor':
      case 'bad':
        return 'var(--color-error)';
      case 'fair':
      case 'average':
        return 'var(--color-warning)';
      default:
        return 'var(--color-text-secondary)';
    }
  };
  
  // Get engagement color
  const getEngagementColor = (engagement) => {
    switch (engagement.toLowerCase()) {
      case 'high':
        return 'var(--color-success)';
      case 'low':
        return 'var(--color-error)';
      case 'medium':
        return 'var(--color-warning)';
      default:
        return 'var(--color-text-secondary)';
    }
  };
  
  return (
    <RelationshipContainer>
      <MetricsContainer>
        <MetricItem>
          <MetricLabel>Relationship Quality</MetricLabel>
          <MetricValue color={getQualityColor(data.quality)}>
            {data.quality}
          </MetricValue>
        </MetricItem>
        
        <MetricItem>
          <MetricLabel>Communication</MetricLabel>
          <MetricValue color={getCommunicationColor(data.communication)}>
            {data.communication}
          </MetricValue>
        </MetricItem>
        
        <MetricItem>
          <MetricLabel>Engagement</MetricLabel>
          <MetricValue color={getEngagementColor(data.engagement)}>
            {data.engagement}
          </MetricValue>
        </MetricItem>
      </MetricsContainer>
      
      {data.topics && data.topics.length > 0 && (
        <Section>
          <SectionTitle>Common Topics</SectionTitle>
          <TopicsList>
            {data.topics.map((topic, index) => (
              <TopicItem key={index}>
                {topic}
              </TopicItem>
            ))}
          </TopicsList>
        </Section>
      )}
      
      {data.recommendations && data.recommendations.length > 0 && (
        <Section>
          <SectionTitle>Recommendations</SectionTitle>
          <RecommendationsList>
            {data.recommendations.map((recommendation, index) => (
              <RecommendationItem key={index}>
                {recommendation}
              </RecommendationItem>
            ))}
          </RecommendationsList>
        </Section>
      )}
      
      {data.summary && (
        <Section>
          <SectionTitle>Summary</SectionTitle>
          <SummaryText>{data.summary}</SummaryText>
        </Section>
      )}
    </RelationshipContainer>
  );
};

// Styled components
const RelationshipContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const MetricsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
`;

const MetricItem = styled.div`
  display: flex;
  flex-direction: column;
`;

const MetricLabel = styled.div`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
`;

const MetricValue = styled.div`
  font-size: var(--font-size-md);
  font-weight: bold;
  color: ${props => props.color};
`;

const Section = styled.div`
  margin-bottom: var(--spacing-lg);
`;

const SectionTitle = styled.h4`
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm) 0;
`;

const TopicsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
`;

const TopicItem = styled.div`
  background-color: var(--color-surface-variant);
  color: var(--color-text-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
`;

const RecommendationsList = styled.ul`
  margin: 0;
  padding-left: var(--spacing-lg);
`;

const RecommendationItem = styled.li`
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-sm);
  line-height: 1.5;
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

export default RelationshipAnalysis;