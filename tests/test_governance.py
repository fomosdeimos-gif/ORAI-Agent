"""Testes para sistema de governance"""
import pytest
from datetime import datetime
from src.governance.dao import GovernanceDAO, ProposalStatus
from src.governance.veto_council import VetoCouncil

@pytest.fixture
def dao():
    """Fixture para DAO"""
    token_holders = {
        'alice': 1000,
        'bob': 500,
        'charlie': 300,
        'dave': 200
    }
    return GovernanceDAO(token_holders)

def test_create_proposal(dao):
    """Testa criação de proposta"""
    proposal_id = dao.create_proposal(
        title="Aumentar frequência de ciclos",
        description="Aumentar para 60 segundos",
        proposer="alice",
        proposal_type="parameter_update",
        target_parameter="CYCLE_INTERVAL",
        new_value="60"
    )
    assert proposal_id.startswith("prop_")
    assert proposal_id in dao.proposals

def test_create_proposal_insufficient_tokens(dao):
    """Testa rejeição de proposta sem tokens suficientes"""
    with pytest.raises(ValueError):
        dao.create_proposal(
            title="Test",
            description="Test",
            proposer="unknown",
            proposal_type="test"
        )

def test_vote(dao):
    """Testa votação em proposta"""
    proposal_id = dao.create_proposal(
        title="Test",
        description="Test",
        proposer="alice",
        proposal_type="test"
    )
    
    # Alice vota a favor
    dao.vote("alice", proposal_id, "for")
    proposal = dao.proposals[proposal_id]
    assert proposal.votes_for == 1000
    
    # Bob vota contra
    dao.vote("bob", proposal_id, "against")
    assert proposal.votes_against == 500

def test_double_vote_prevention(dao):
    """Testa prevenção de voto duplo"""
    proposal_id = dao.create_proposal(
        title="Test",
        description="Test",
        proposer="alice",
        proposal_type="test"
    )
    
    dao.vote("alice", proposal_id, "for")
    
    with pytest.raises(ValueError):
        dao.vote("alice", proposal_id, "for")

def test_veto_council():
    """Testa conselho de veto"""
    council = VetoCouncil(
        council_members=['alice', 'bob', 'charlie'],
        required_signatures=2
    )
    
    # Propor veto
    council.propose_veto('alice', 'prop_1', 'Emergency action')
    assert not council.is_vetoed('prop_1')
    
    # Primeira assinatura
    council.sign_veto('bob', 'prop_1')
    assert not council.is_vetoed('prop_1')
    
    # Segunda assinatura (quórum atingido)
    council.sign_veto('charlie', 'prop_1')
    assert council.is_vetoed('prop_1')

def test_get_proposal_status(dao):
    """Testa obtenção de status de proposta"""
    proposal_id = dao.create_proposal(
        title="Test Proposal",
        description="Testing status",
        proposer="alice",
        proposal_type="test"
    )
    
    dao.vote("alice", proposal_id, "for")
    dao.vote("bob", proposal_id, "against")
    
    status = dao.get_proposal_status(proposal_id)
    assert status['title'] == "Test Proposal"
    assert status['votes_for'] == 1000
    assert status['votes_against'] == 500
    assert status['total_votes'] == 1500

def test_treasury_balance(dao):
    """Testa saldo da tesoura"""
    balance = dao.get_treasury_balance()
    assert balance == 2000  # 1000 + 500 + 300 + 200

def test_distribute_rewards(dao):
    """Testa distribuição de recompensas"""
    initial = dao.token_holders['alice']
    dao.distribute_rewards(100, 'alice')
    assert dao.token_holders['alice'] == initial + 100
