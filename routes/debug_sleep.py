# debug_sleep.py - Script to debug sleep data availability
import httpx
import asyncio
from datetime import datetime, timedelta
import json

async def debug_sleep_data(access_token):
    """Debug function to check what sleep data is available"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    start_time_millis = int(start_time.timestamp() * 1000)
    end_time_millis = int(end_time.timestamp() * 1000)
    
    print("=" * 50)
    print("SLEEP DATA DEBUG REPORT")
    print("=" * 50)
    print(f"Time range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    async with httpx.AsyncClient() as client:
        
        # 1. Check available data sources
        print("1. CHECKING AVAILABLE DATA SOURCES:")
        print("-" * 30)
        
        try:
            sources_response = await client.get(
                'https://www.googleapis.com/fitness/v1/users/me/dataSources',
                headers=headers
            )
            
            if sources_response.status_code == 200:
                sources = sources_response.json()
                sleep_sources = [s for s in sources.get('dataSource', []) if 'sleep' in s.get('dataStreamId', '').lower()]
                
                print(f"Found {len(sleep_sources)} sleep-related data sources:")
                for i, source in enumerate(sleep_sources):
                    print(f"  {i+1}. {source.get('dataStreamId', 'Unknown')}")
                    print(f"     Type: {source.get('dataType', {}).get('name', 'Unknown')}")
                    print(f"     Device: {source.get('device', {}).get('model', 'Unknown')}")
                    print()
            else:
                print(f"❌ Error fetching data sources: {sources_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking data sources: {e}")
        
        # 2. Check sleep sessions
        print("2. CHECKING SLEEP SESSIONS:")
        print("-" * 30)
        
        try:
            sessions_params = {
                'startTime': start_time.isoformat() + 'Z',
                'endTime': end_time.isoformat() + 'Z',
                'activityType': '72'  # Sleep activity type
            }
            
            sessions_response = await client.get(
                'https://www.googleapis.com/fitness/v1/users/me/sessions',
                headers=headers,
                params=sessions_params
            )
            
            if sessions_response.status_code == 200:
                sessions_data = sessions_response.json()
                sessions = sessions_data.get('session', [])
                
                print(f"Found {len(sessions)} sleep sessions:")
                for i, session in enumerate(sessions):
                    start_ms = int(session.get('startTimeMillis', 0))
                    end_ms = int(session.get('endTimeMillis', 0))
                    start_dt = datetime.fromtimestamp(start_ms / 1000)
                    end_dt = datetime.fromtimestamp(end_ms / 1000)
                    duration = (end_ms - start_ms) / (1000 * 60 * 60)  # hours
                    
                    print(f"  {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
                    print(f"     Duration: {duration:.1f} hours")
                    print(f"     ID: {session.get('id', 'Unknown')}")
                    print()
            else:
                print(f"❌ Error fetching sleep sessions: {sessions_response.status_code}")
                print(f"Response: {sessions_response.text}")
                
        except Exception as e:
            print(f"❌ Error checking sleep sessions: {e}")
        
        # 3. Try direct sleep data access
        print("3. CHECKING DIRECT SLEEP DATA ACCESS:")
        print("-" * 30)
        
        sleep_data_sources = [
            "derived:com.google.sleep.segment:com.google.android.gms:merged",
            "raw:com.google.sleep.segment:com.google.android.gms:merged",
            "derived:com.google.sleep.segment:com.google.android.gms:platform_merge"
        ]
        
        for source in sleep_data_sources:
            try:
                dataset_url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/{source}/datasets/{start_time_millis}-{end_time_millis}"
                
                dataset_response = await client.get(dataset_url, headers=headers)
                
                print(f"Source: {source}")
                print(f"Status: {dataset_response.status_code}")
                
                if dataset_response.status_code == 200:
                    dataset = dataset_response.json()
                    points = dataset.get('point', [])
                    print(f"Data points: {len(points)}")
                    
                    if points:
                        print("Sample data points:")
                        for i, point in enumerate(points[:3]):  # Show first 3 points
                            start_ns = int(point.get('startTimeNanos', 0))
                            end_ns = int(point.get('endTimeNanos', 0))
                            start_dt = datetime.fromtimestamp(start_ns / 1e9)
                            end_dt = datetime.fromtimestamp(end_ns / 1e9)
                            value = point.get('value', [{}])[0].get('intVal', -1)
                            
                            print(f"  Point {i+1}: {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}, Stage: {value}")
                else:
                    print(f"Error: {dataset_response.text}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error accessing {source}: {e}")
                print()
        
        # 4. Check aggregate sleep data
        print("4. CHECKING AGGREGATE SLEEP DATA:")
        print("-" * 30)
        
        try:
            aggregate_data = {
                "aggregateBy": [
                    {"dataTypeName": "com.google.sleep.segment"}
                ],
                "bucketByTime": {"durationMillis": 86400000},  # 1 day buckets
                "startTimeMillis": start_time_millis,
                "endTimeMillis": end_time_millis
            }
            
            aggregate_response = await client.post(
                'https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate',
                headers=headers,
                json=aggregate_data
            )
            
            print(f"Aggregate API Status: {aggregate_response.status_code}")
            
            if aggregate_response.status_code == 200:
                aggregate_result = aggregate_response.json()
                buckets = aggregate_result.get('bucket', [])
                
                print(f"Found {len(buckets)} daily buckets:")
                for i, bucket in enumerate(buckets):
                    bucket_start = datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000)
                    datasets = bucket.get('dataset', [])
                    
                    total_points = sum(len(ds.get('point', [])) for ds in datasets)
                    print(f"  {bucket_start.strftime('%Y-%m-%d')}: {total_points} data points")
            else:
                print(f"Error: {aggregate_response.text}")
                
        except Exception as e:
            print(f"❌ Error checking aggregate data: {e}")

# Add this function to your main application for debugging
async def run_sleep_debug(credentials_dict):
    """Run sleep debug with your credentials"""
    from services.googlefit import google_fit_service
    
    creds = google_fit_service.credentials_from_dict(credentials_dict)
    creds = google_fit_service.refresh_credentials_if_needed(creds)
    
    await debug_sleep_data(creds.token)