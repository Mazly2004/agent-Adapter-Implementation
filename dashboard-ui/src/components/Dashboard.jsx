import React from 'react';
import ResponseCard from './ResponseCard';

const Dashboard = ({ initialResponse, rewrittenResponse, question, sentiment, selfCheckResult }) => {
    return (
        <div className="dashboard">
            <h1>Dashboard</h1>
            <div className="response-section">
                <h2>Input Question</h2>
                <p>{question}</p>
            </div>
            <ResponseCard 
                title="Initial Response" 
                response={initialResponse} 
                sentiment={sentiment} 
                selfCheckResult={selfCheckResult} 
            />
            {rewrittenResponse && (
                <ResponseCard 
                    title="Rewritten Response" 
                    response={rewrittenResponse} 
                    sentiment={sentiment} 
                    selfCheckResult={selfCheckResult} 
                />
            )}
        </div>
    );
};

export default Dashboard;