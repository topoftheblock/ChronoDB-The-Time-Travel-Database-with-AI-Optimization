import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

class MLOptimizer:
    def __init__(self):
        self.model = None
        self.training_data = []
        self.feature_names = [
            'table_size', 'filter_selectivity', 'join_complexity', 
            'index_presence', 'memory_available', 'query_complexity'
        ]
    
    def extract_features(self, query_plan, system_stats):
        """Extract features from query plan for ML model"""
        features = {
            'table_size': sum(t.size for t in query_plan.tables),
            'filter_selectivity': self.estimate_selectivity(query_plan.where_clause),
            'join_complexity': len(query_plan.joins),
            'index_presence': int(any(t.has_index for t in query_plan.tables)),
            'memory_available': system_stats.available_memory,
            'query_complexity': len(query_plan.operations)
        }
        return np.array([features[f] for f in self.feature_names])
    
    def predict_optimal_plan(self, query_plans, system_stats):
        """Use ML to choose the best query plan"""
        if not self.model:
            return query_plans[0]  # Fallback to first plan
            
        best_plan = None
        best_score = float('inf')
        
        for plan in query_plans:
            features = self.extract_features(plan, system_stats).reshape(1, -1)
            predicted_cost = self.model.predict(features)[0]
            
            if predicted_cost < best_score:
                best_score = predicted_cost
                best_plan = plan
                
        return best_plan
    
    def learn_from_feedback(self, actual_plan, actual_execution_time):
        """Reinforcement learning: learn from actual query performance"""
        features = self.extract_features(actual_plan.original_plan, actual_plan.system_stats)
        self.training_data.append((features, actual_execution_time))
        
        # Retrain model periodically
        if len(self.training_data) % 100 == 0:
            self.retrain_model()
    
    def retrain_model(self):
        """Retrain the ML model with new data"""
        if len(self.training_data) < 10:
            return
            
        X = np.array([data[0] for data in self.training_data])
        y = np.array([data[1] for data in self.training_data])
        
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(X, y)
        
        # Save model for persistence
        with open('query_optimizer_model.pkl', 'wb') as f:
            pickle.dump(self.model, f)