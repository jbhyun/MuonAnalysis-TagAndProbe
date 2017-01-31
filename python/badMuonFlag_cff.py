import FWCore.ParameterSet.Config as cms


badGlobalMuonTagger = cms.EDFilter("BadGlobalMuonTagger",
    muons = cms.InputTag("muons"),
    vtx   = cms.InputTag("offlinePrimaryVertices"),
    muonPtCut = cms.double(20),
    selectClones = cms.bool(False),
    taggingMode = cms.bool(True),
)
cloneGlobalMuonTagger = badGlobalMuonTagger.clone(
    selectClones = True
)

flagBadGlobalMuons = cms.Sequence(cloneGlobalMuonTagger + badGlobalMuonTagger)
