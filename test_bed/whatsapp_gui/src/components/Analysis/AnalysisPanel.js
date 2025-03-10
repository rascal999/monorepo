import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useApp } from '../../context/AppContext';
import ollama from '../../services/ollama';
import SentimentAnalysis from './SentimentAnalysis';
import RelationshipAnalysis from './RelationshipAnalysis';
import SuggestedResponses from './SuggestedResponses';

/**
 * Panel for displaying message analysis
 */
const AnalysisPanel = () => {
  const { 
    activeChat, 
    messages, 
    analysisResults, 
    setAnalysisResults,
    toggleAnalysisPanel
  } = useApp();
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('sentiment');
  
  // Analyze messages when they change
  useEffect(() => {
    if (!messages || messages.length === 0) return;
    
    // Only analyze if we have enough messages
    if (messages.length < 3) return;
    
    // Limit to last 20 messages for analysis
    const messagesToAnalyze = messages.slice(0, 20);
    
    const performAnalysis = async () => {
      setIsAnalyzing(true);
      
      try {
        // Analyze sentiment
        const sentimentResult = await ollama.analyzeSentiment(messagesToAnalyze);
        let sentimentData = {};
        
        try {
          sentimentData = JSON.parse(sentimentResult);
        } catch (error) {
          console.error('Error parsing sentiment analysis:', error);
          sentimentData = {
            sentiment: 'unknown',
            score: 5,
            emotions: [],
            summary: 'Unable to analyze sentiment'
          };
        }
        
        // Analyze relationship
        const relationshipResult = await ollama.analyzeRelationship(messagesToAnalyze);
        let relationshipData = {};
        
        try {
          relationshipData = JSON.parse(relationshipResult);
        } catch (error) {
          console.error('Error parsing relationship analysis:', error);
          relationshipData = {
            quality: 'unknown',
            communication: 'unknown',
            engagement: 'unknown',
            topics: [],
            recommendations: [],
            summary: 'Unable to analyze relationship'
          };
        }
        
        // Generate suggested responses
        const responsesResult = await ollama.generateResponses(messagesToAnalyze, 3);
        let responsesData = { responses: [] };
        
        try {
          responsesData = JSON.parse(responsesResult);
        } catch (error) {
          console.error('Error parsing suggested responses:', error);
          responsesData = {
            responses: [
              {
                text: 'I understand.',
                tone: 'neutral',
                purpose: 'acknowledgment'
              }
            ]
          };
        }
        
        // Update analysis results
        setAnalysisResults({
          sentiment: sentimentData,
          relationship: relationshipData,
          suggestedResponses: responsesData.responses
        });
      } catch (error) {
        console.error('Error performing analysis:', error);
      } finally {
        setIsAnalyzing(false);
      }
    };
    
    // Debounce analysis to avoid too many requests
    const debounceTimeout = setTimeout(() => {
      performAnalysis();
    }, 1000);
    
    return () => clearTimeout(debounceTimeout);
  }, [messages, setAnalysisResults]);
  
  // Switch between tabs
  const switchTab = (tab) => {
    setActiveTab(tab);
  };
  
  return (
    <AnalysisPanelContainer>
      <PanelHeader>
        <PanelTitle>Conversation Analysis</PanelTitle>
        <CloseButton onClick={toggleAnalysisPanel}>✕</CloseButton>
      </PanelHeader>
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'sentiment'} 
          onClick={() => switchTab('sentiment')}
        >
          Sentiment
        </Tab>
        <Tab 
          active={activeTab === 'relationship'} 
          onClick={() => switchTab('relationship')}
        >
          Relationship
        </Tab>
        <Tab 
          active={activeTab === 'responses'} 
          onClick={() => switchTab('responses')}
        >
          Responses
        </Tab>
      </TabsContainer>
      
      <PanelContent>
        {isAnalyzing ? (
          <LoadingContainer>
            <LoadingSpinner />
            <LoadingText>Analyzing conversation...</LoadingText>
          </LoadingContainer>
        ) : (
          <>
            {activeTab === 'sentiment' && (
              <SentimentAnalysis data={analysisResults.sentiment} />
            )}
            
            {activeTab === 'relationship' && (
              <RelationshipAnalysis data={analysisResults.relationship} />
            )}
            
            {activeTab === 'responses' && (
              <SuggestedResponses 
                responses={analysisResults.suggestedResponses} 
              />
            )}
          </>
        )}
      </PanelContent>
    </AnalysisPanelContainer>
  );
};

// Styled components
const AnalysisPanelContainer = styled.div`
  width: 300px;
  height: 100%;
  background-color: var(--color-surface);
  border-left: 1px solid var(--color-divider);
  display: flex;
  flex-direction: column;
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--color-surface-variant);
  height: 60px;
`;

const PanelTitle = styled.h2`
  font-size: var(--font-size-md);
  margin: 0;
  color: var(--color-primary);
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-md);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: var(--color-text-primary);
  }
`;

const TabsContainer = styled.div`
  display: flex;
  border-bottom: 1px solid var(--color-divider);
`;

const Tab = styled.button`
  flex: 1;
  padding: var(--spacing-sm);
  background: none;
  border: none;
  border-bottom: 2px solid ${props => 
    props.active ? 'var(--color-primary)' : 'transparent'};
  color: ${props => 
    props.active ? 'var(--color-primary)' : 'var(--color-text-secondary)'};
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
  
  &:hover {
    background-color: var(--color-surface-variant);
  }
`;

const PanelContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
`;

const LoadingSpinner = styled.div`
  width: 30px;
  height: 30px;
  border: 3px solid var(--color-surface-variant);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.p`
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  text-align: center;
`;

export default AnalysisPanel;