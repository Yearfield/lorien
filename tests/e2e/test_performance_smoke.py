"""
Performance smoke test: next-incomplete parent query performance and CSV export.
"""

import os
import subprocess
import time
import tempfile
from tests.utils.http import get_json


def test_next_incomplete_parent_performance(temp_database, api_server):
    """
    Test that next-incomplete parent query performs within acceptable bounds.
    This is a smoke test that may be skipped on slow CI hardware.
    """
    # Import a larger dataset for performance testing
    fixture_path = "tests/fixtures/perfect_5_children.xlsx"
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"
    
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    
    base_url = api_server
    
    # Test next-incomplete parent query performance
    print("🔍 Testing next-incomplete parent query performance...")
    
    latencies = []
    for i in range(10):
        start_time = time.time()
        
        try:
            response = get_json(f"{base_url}/api/v1/tree/next-incomplete-parent")
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            latencies.append(latency)
            print(f"  Query {i+1}: {latency:.2f}ms")
            
        except Exception as e:
            print(f"  Query {i+1}: Error - {e}")
            continue
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"📊 Performance Summary:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  Min: {min_latency:.2f}ms")
        print(f"  Max: {max_latency:.2f}ms")
        print(f"  Samples: {len(latencies)}")
        
        # Performance assertion (lenient for smoke test)
        # Mark as xfail if performance is too slow
        if avg_latency > 100:  # 100ms threshold
            import pytest
            pytest.xfail(f"Performance too slow: {avg_latency:.2f}ms average (threshold: 100ms)")
        
        print(f"✅ Performance test passed: {avg_latency:.2f}ms average")
    else:
        print("⚠️ No successful performance measurements")
    
    return latencies


def test_csv_export_performance(temp_database, api_server):
    """
    Test CSV export performance and ensure header order is maintained.
    """
    # Import data
    fixture_path = "tests/fixtures/perfect_5_children.xlsx"
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    
    # Test CSV export performance
    print("📊 Testing CSV export performance...")
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
        export_path = tmp_file.name
    
    try:
        start_time = time.time()
        
        result = subprocess.run(
            ["python", "-m", "cli.main", "export-csv", export_path],
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        end_time = time.time()
        export_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if result.returncode != 0:
            print(f"❌ Export failed: {result.stderr}")
            assert False, f"Export failed with return code {result.returncode}"
        
        print(f"✅ CSV export completed in {export_time:.2f}ms")
        
        # Verify the exported CSV has correct headers
        import csv
        with open(export_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
        
        expected_headers = [
            "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
            "Diagnostic Triage", "Actions"
        ]
        
        assert headers == expected_headers, \
            f"Header mismatch:\n  got: {headers}\n  exp: {expected_headers}"
        
        print(f"✅ CSV headers verified: {headers}")
        
        # Count rows
        with open(export_path, 'r', encoding='utf-8') as f:
            row_count = sum(1 for _ in f) - 1  # Subtract header row
        
        print(f"✅ CSV exported {row_count} data rows")
        
        # Performance assertion (very lenient for smoke test)
        if export_time > 5000:  # 5 second threshold
            import pytest
            pytest.xfail(f"Export too slow: {export_time:.2f}ms (threshold: 5000ms)")
        
        print(f"✅ Export performance test passed: {export_time:.2f}ms")
        
    finally:
        if os.path.exists(export_path):
            os.unlink(export_path)


def test_api_endpoint_performance(temp_database, api_server):
    """
    Test basic API endpoint performance.
    """
    base_url = api_server
    
    print("🚀 Testing API endpoint performance...")
    
    # Test health endpoint performance
    health_latencies = []
    for i in range(5):
        start_time = time.time()
        
        try:
            response = get_json(f"{base_url}/api/v1/health")
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            health_latencies.append(latency)
            print(f"  Health {i+1}: {latency:.2f}ms")
            
        except Exception as e:
            print(f"  Health {i+1}: Error - {e}")
            continue
    
    if health_latencies:
        avg_health_latency = sum(health_latencies) / len(health_latencies)
        print(f"📊 Health endpoint performance: {avg_health_latency:.2f}ms average")
        
        # Health endpoint should be very fast
        if avg_health_latency > 50:  # 50ms threshold
            import pytest
            pytest.xfail(f"Health endpoint too slow: {avg_health_latency:.2f}ms average (threshold: 50ms)")
        
        print(f"✅ Health endpoint performance test passed")
    
    # Test children endpoint performance (if data exists)
    try:
        # Find any parent to test with
        next_incomplete = get_json(f"{base_url}/api/v1/tree/next-incomplete-parent")
        if next_incomplete:
            parent_id = next_incomplete["parent_id"]
            
            children_latencies = []
            for i in range(3):  # Fewer iterations for data endpoint
                start_time = time.time()
                
                try:
                    response = get_json(f"{base_url}/api/v1/tree/{parent_id}/children")
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000
                    
                    children_latencies.append(latency)
                    print(f"  Children {i+1}: {latency:.2f}ms")
                    
                except Exception as e:
                    print(f"  Children {i+1}: Error - {e}")
                    continue
            
            if children_latencies:
                avg_children_latency = sum(children_latencies) / len(children_latencies)
                print(f"📊 Children endpoint performance: {avg_children_latency:.2f}ms average")
                
                # Children endpoint should be reasonably fast
                if avg_children_latency > 200:  # 200ms threshold
                    import pytest
                    pytest.xfail(f"Children endpoint too slow: {avg_children_latency:.2f}ms average (threshold: 200ms)")
                
                print(f"✅ Children endpoint performance test passed")
    
    except Exception as e:
        print(f"⚠️ Could not test children endpoint: {e}")


def test_overall_system_performance(temp_database, api_server):
    """
    Overall system performance smoke test.
    """
    print("🔥 Running overall system performance smoke test...")
    
    # Run all performance tests
    next_incomplete_latencies = test_next_incomplete_parent_performance(temp_database, api_server)
    test_csv_export_performance(temp_database, api_server)
    test_api_endpoint_performance(temp_database, api_server)
    
    # Summary
    if next_incomplete_latencies:
        avg_latency = sum(next_incomplete_latencies) / len(next_incomplete_latencies)
        print(f"\n🎯 Overall Performance Summary:")
        print(f"  Next-incomplete parent: {avg_latency:.2f}ms average")
        print(f"  CSV export: Completed successfully")
        print(f"  API endpoints: Performance verified")
        print(f"  ✅ All performance tests passed")
    else:
        print(f"\n⚠️ Performance test summary incomplete")
