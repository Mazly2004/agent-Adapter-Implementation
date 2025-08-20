import React from 'react';

const ResponseCard = ({ question, initialResponse, rewrittenResponse, sentiment, selfCheckResult }) => {
    return (
        <div className="response-card">
            <h3>Input Question</h3>
            <p>{question}</p>
            <h3>Initial Response</h3>
            <div >
                <p>{initialResponse}</p>
            </div>
            
            {rewrittenResponse && (
                <div >
                    <h3>Rewritten Response</h3>
                    <p>{rewrittenResponse}</p>
                </div>
            )}
            <h3>Sentiment</h3>
            <p>{sentiment}</p>
            <h3>Self-Check Status</h3>
            <p>{selfCheckResult}</p>
        </div>
    );
};

export default ResponseCard;