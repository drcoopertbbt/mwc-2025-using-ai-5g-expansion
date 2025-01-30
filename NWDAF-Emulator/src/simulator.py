from flask import Flask, render_template, jsonify
import json
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates')

def generate_nwdaf_data(num_records=20):
    verticals = {
        'consumer': {
            'services': [
                'video_streaming',
                'online_gaming',
                'voice_calls',
                'social_media',
                'web_browsing'
            ],
            'weight': 0.4  # 40% of traffic (common 5G usage)
        },
        'healthcare': {
            'services': [
                'remote_surgery',
                'patient_monitoring',
                'medical_imaging',
                'ambulance_telemetry',
                'hospital_IoT'
            ],
            'weight': 0.2  # 20% of traffic (makes healthcare events more notable)
        },
        'industrial': {
            'services': [
                'factory_automation',
                'predictive_maintenance',
                'quality_control',
                'remote_operations',
                'sensor_networks'
            ],
            'weight': 0.2
        },
        'smart_city': {
            'services': [
                'traffic_monitoring',
                'public_safety',
                'environmental_sensors',
                'smart_lighting',
                'waste_management'
            ],
            'weight': 0.2
        }
    }

    # Network performance metrics ranges
    performance_metrics = {
        'latency': {'min': 1, 'max': 20},  # ms
        'throughput': {'min': 100, 'max': 1000},  # Mbps
        'reliability': {'min': 99.9, 'max': 99.999},  # percentage
        'connection_density': {'min': 100, 'max': 1000}  # devices/km2
    }

    segments = {
        'enhanced_mobile_broadband': {'range': (1.0, 2.0), 'threshold': 1.5},
        'ultra_reliable_low_latency': {'range': (2.1, 3.0), 'threshold': 2.5},
        'massive_machine_type': {'range': (3.1, 4.5), 'threshold': 3.5}
    }
    
    records = []
    base_time = datetime.now()
    
    for i in range(num_records):
        # Select vertical based on weights
        vertical = random.choices(
            list(verticals.keys()),
            weights=[v['weight'] for v in verticals.values()]
        )[0]
        
        # Select service from the chosen vertical
        service = random.choice(verticals[vertical]['services'])
        
        # Select segment and determine score within its range
        segment = random.choice(list(segments.keys()))
        score_range = segments[segment]['range']
        predicted_score = round(random.uniform(*score_range), 1)
        
        # Generate network performance metrics
        metrics = {
            'latency': round(random.uniform(
                performance_metrics['latency']['min'],
                performance_metrics['latency']['max']
            ), 1),
            'throughput': round(random.uniform(
                performance_metrics['throughput']['min'],
                performance_metrics['throughput']['max']
            )),
            'reliability': round(random.uniform(
                performance_metrics['reliability']['min'],
                performance_metrics['reliability']['max']
            ), 3),
            'connection_density': round(random.uniform(
                performance_metrics['connection_density']['min'],
                performance_metrics['connection_density']['max']
            ))
        }

        record = {
            'vertical': vertical,
            'service_id': service,
            'segment': segment,
            'predicted_score': predicted_score,
            'timestamp': (base_time + timedelta(minutes=i)).strftime('%Y-%m-%dT%H:%M:%S'),
            'trend': 'increasing' if predicted_score > segments[segment]['threshold'] else 'stable',
            'user_id': random.randint(1000, 9999),
            'metrics': metrics
        }
        records.append(record)
    
    return records

def load_network_slices():
    kb_path = os.path.join(os.path.dirname(__file__), 'data/knowledge_base/support_articles.json')
    with open(kb_path, 'r') as f:
        data = json.load(f)
        return data['network_analytics']

@app.route('/api/nwdaf/data')
def get_nwdaf_data():
    return jsonify(generate_nwdaf_data())

@app.route('/api/nwdaf/slices')
def get_network_slices():
    return jsonify(load_network_slices())

@app.route('/')
def simulator():
    nwdaf_data = generate_nwdaf_data()
    network_slices = load_network_slices()
    return render_template('simulator.html', 
                         nwdaf_data=nwdaf_data,
                         network_slices=network_slices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
