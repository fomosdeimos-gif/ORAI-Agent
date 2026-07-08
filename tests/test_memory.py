"""Testes para sistema de memória"""
import pytest
import os
import tempfile
from src.memory import AutonomousMemory, MemoryEntry

@pytest.fixture
def memory():
    """Fixture para memória autônoma"""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_path = os.path.join(tmpdir, 'memory.json')
        yield AutonomousMemory(memory_path)

def test_memory_entry():
    """Testa dataclass de entrada"""
    entry = MemoryEntry(
        id='test1',
        cycle_number=1,
        strategy_name='YieldFarming',
        revenue_generated=0.1,
        success=True,
        timestamp='2024-01-01',
        metadata={}
    )
    assert entry.cycle_number == 1
    assert entry.success

def test_record_cycle(memory):
    """Testa registro de ciclo"""
    results = [
        {
            'strategy_name': 'YieldFarming',
            'revenue_generated': 0.1,
            'success': True,
            'transactions': ['0xabc'],
            'error': None
        }
    ]
    memory.record_cycle(1, results, 0.1)
    assert len(memory.memory) == 1

def test_performance_stats(memory):
    """Testa estatísticas de performance"""
    results = [
        {
            'strategy_name': 'YieldFarming',
            'revenue_generated': 0.1,
            'success': True,
            'transactions': [],
            'error': None
        }
    ]
    memory.record_cycle(1, results, 0.1)
    
    stats = memory.get_performance_stats()
    assert stats['total_revenue_generated'] == 0.1
    assert stats['success_rate'] == 1.0
