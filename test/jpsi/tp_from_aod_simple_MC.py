import FWCore.ParameterSet.Config as cms

process = cms.Process("TagProbe")

process.load('FWCore.MessageService.MessageLogger_cfi')
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring(
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0048/5256A51F-B70D-E011-BF95-002618943836.root',
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0047/FAB16CB1-910D-E011-941A-003048678A6A.root',
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0047/D697B653-8E0D-E011-9E44-002618FDA277.root',
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0047/6E1B7762-8F0D-E011-BCA8-00304867C1B0.root',
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0047/5E79B339-8D0D-E011-A842-0026189438F5.root',
	'/store/relval/CMSSW_3_9_7/RelValJpsiMM/GEN-SIM-RECO/START39_V8-v1/0047/3A073491-960D-E011-9732-002354EF3BE0.root',
    ),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )    


process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.GlobalTag.globaltag = cms.string('START39_V8::All')

## ==== Fast Filters ====
process.goodVertexFilter = cms.EDFilter("VertexSelector",
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake && ndof > 4 && abs(z) <= 25 && position.Rho <= 2"),
    filter = cms.bool(True),
)
process.noScraping = cms.EDFilter("FilterOutScraping",
    applyfilter = cms.untracked.bool(True),
    debugOn = cms.untracked.bool(False), ## Or 'True' to get some per-event info
    numtrack = cms.untracked.uint32(10),
    thresh = cms.untracked.double(0.25)
)
process.fastFilter = cms.Sequence(process.goodVertexFilter + process.noScraping)

process.load("HLTrigger.HLTfilters.triggerResultsFilter_cfi")
process.triggerResultsFilter.triggerConditions = cms.vstring( 'HLT_Jet*' )
process.triggerResultsFilter.l1tResults = ''
process.triggerResultsFilter.throw = True
process.triggerResultsFilter.hltResults = cms.InputTag( "TriggerResults", "", "HLT" )
process.HLTMu   = process.triggerResultsFilter.clone(triggerConditions = [ 'HLT_Mu*_L2Mu0' ])
process.HLTBoth = process.triggerResultsFilter.clone(triggerConditions = [ 'HLT_Mu*_L2Mu0', 'HLT_Mu3_Track*_Jpsi*', 'HLT_Mu5_Track*_Jpsi*' ])


## ==== Merge CaloMuons and Tracks into the collection of reco::Muons  ====
from RecoMuon.MuonIdentification.calomuons_cfi import calomuons;
process.mergedMuons = cms.EDProducer("CaloMuonMerger",
    mergeTracks = cms.bool(True),
    muons     = cms.InputTag("muons"), 
    caloMuons = cms.InputTag("calomuons"),
    tracks    = cms.InputTag("generalTracks"),
    minCaloCompatibility = calomuons.minCaloCompatibility,
    ## Apply some minimal pt cut
    muonsCut     = cms.string("track.isNonnull"),
    caloMuonsCut = cms.string(""),
    tracksCut    = cms.string("pt > 2 || (abs(eta) > 1 && p > 2)"),
)

## ==== Trigger matching
process.load("MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff")
## with some customization
from MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff import *
changeRecoMuonInput(process, "mergedMuons")
#useL1MatchingWindowForSinglets(process) ## No longer used
changeTriggerProcessName(process, "*")

from MuonAnalysis.TagAndProbe.common_variables_cff import *
process.load("MuonAnalysis.TagAndProbe.common_modules_cff")

process.tagMuons = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("patMuonsWithTrigger"),
    cut = cms.string("isGlobalMuon  && pt > 3 && !triggerObjectMatchesByCollection('hltL3MuonCandidates').empty()"),
)

process.oneTag  = cms.EDFilter("CandViewCountFilter", src = cms.InputTag("tagMuons"), minNumber = cms.uint32(1))

process.probeMuons = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("patMuonsWithTrigger"),
    cut = cms.string("track.isNonnull && (!triggerObjectMatchesByCollection('hltMuTrackJpsiCtfTrackCands').empty() || !triggerObjectMatchesByCollection('hltL2MuonCandidates').empty())"),
)

process.tpPairs = cms.EDProducer("CandViewShallowCloneCombiner",
    cut = cms.string('2.8 < mass < 3.4'),
    decay = cms.string('tagMuons@+ probeMuons@-')
)
process.onePair = cms.EDFilter("CandViewCountFilter", src = cms.InputTag("tpPairs"), minNumber = cms.uint32(1))

process.tagMuonsMCMatch = cms.EDProducer("MCTruthDeltaRMatcherNew",
    src = cms.InputTag("tagMuons"),
    matched = cms.InputTag("genParticles"),
    pdgId = cms.vint32(13),
    distMin = cms.double(0.3),
)
process.probeMuonsMCMatch = process.tagMuonsMCMatch.clone(src = "probeMuons")


process.tpTree = cms.EDAnalyzer("TagProbeFitTreeProducer",
    # choice of tag and probe pairs, and arbitration
    tagProbePairs = cms.InputTag("tpPairs"),
    arbitration   = cms.string("OneProbe"),
    # probe variables: all useful ones
    variables = cms.PSet(
        AllVariables,
        dxyPVdzmin = cms.InputTag("muonDxyPVdzmin","dxyPVdzmin"),
    ),
    flags = cms.PSet(
       TrackQualityFlags,
       MuonIDFlags,
       HighPtTriggerFlags,
       LowPtTriggerFlagsPhysics,
       LowPtTriggerFlagsEfficienciesProbe,
       ## ParticleFlow
       PF = cms.InputTag("muonsPassingPF"),
       ## A few other flags
       Track_QTF  = cms.string("track.numberOfValidHits > 11 && track.hitPattern.pixelLayersWithMeasurement > 1 && track.normalizedChi2 < 4 && abs(dB) < 3 && abs(track.dz) < 30"),
       Track_VBTF = cms.string("track.numberOfValidHits > 10 && track.hitPattern.pixelLayersWithMeasurement > 0 && abs(dB) < 0.2"),
       ## Acceptance definition
       Acc_JPsi = cms.string("(abs(eta) <= 1.3 && pt > 3.3) || (1.3 < abs(eta) <= 2.2 && p > 2.9) || (2.2 < abs(eta) <= 2.4  && pt > 0.8)"),
    ),
    tagVariables = cms.PSet(
        pt  = cms.string('pt'),
        eta = cms.string('eta'),
        nVertices = cms.InputTag("nverticesModule"),
    ),
    tagFlags     = cms.PSet(
        LowPtTriggerFlagsPhysics,
        LowPtTriggerFlagsEfficienciesTag,
    ),
    pairVariables = cms.PSet(
        pt = cms.string("pt"),
        dphiVtxTimesQ = cms.InputTag("tagProbeSeparation", "dphiVtxTimesQ"),
        drM2          = cms.InputTag("tagProbeSeparation", "drM2"),
        dphiM2        = cms.InputTag("tagProbeSeparation", "dphiM2"),
        distM2        = cms.InputTag("tagProbeSeparation", "distM2"),
        drVtx         = cms.InputTag("tagProbeSeparation", "drVtx"),
    ),
    pairFlags = cms.PSet(),
    isMC           = cms.bool(True),
    tagMatches       = cms.InputTag("tagMuonsMCMatch"),
    probeMatches     = cms.InputTag("probeMuonsMCMatch"),
    motherPdgId      = cms.vint32(443),
    makeMCUnbiasTree       = cms.bool(False),
    checkMotherInUnbiasEff = cms.bool(True),
    allProbes              = cms.InputTag("probeMuons"),
)
process.tnpSimpleSequence = cms.Sequence(
    process.tagMuons   * process.tagMuonsMCMatch   +
    process.oneTag     +
    process.probeMuons * process.probeMuonsMCMatch +
    process.tpPairs    +
    process.onePair    +
    process.muonDxyPVdzmin +
    process.nverticesModule +
    process.tagProbeSeparation +
    process.muonsPassingPF +
    process.tpTree
)

process.tagAndProbe = cms.Path( 
    process.fastFilter +
    process.HLTBoth    +
    process.mergedMuons                 *
    process.patMuonsWithTriggerSequence *
    process.tnpSimpleSequence
)

##    _____               _    _             
##   |_   _| __ __ _  ___| | _(_)_ __   __ _ 
##     | || '__/ _` |/ __| |/ / | '_ \ / _` |
##     | || | | (_| | (__|   <| | | | | (_| |
##     |_||_|  \__,_|\___|_|\_\_|_| |_|\__, |
##                                     |___/ 

## Then make another collection for standalone muons, using standalone track to define the 4-momentum
process.muonsSta = cms.EDProducer("RedefineMuonP4FromTrack",
    src   = cms.InputTag("muons"),
    track = cms.string("outer"),
)
## Match to trigger, to measure the efficiency of HLT tracking
from PhysicsTools.PatAlgos.tools.helpers import *
process.patMuonsWithTriggerSequenceSta = cloneProcessingSnippet(process, process.patMuonsWithTriggerSequence, "Sta")
process.muonMatchHLTL2Sta.maxDeltaR = 0.5
process.muonMatchHLTL3Sta.maxDeltaR = 0.5
massSearchReplaceAnyInputTag(process.patMuonsWithTriggerSequenceSta, "mergedMuons", "muonsSta")

## Define probes and T&P pairs
process.probeMuonsSta = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("patMuonsWithTriggerSta"),
    cut = cms.string("outerTrack.isNonnull && !triggerObjectMatchesByCollection('hltL2MuonCandidates').empty()"), 
)
process.probeMuonsMCMatchSta = process.tagMuonsMCMatch.clone(src = "probeMuonsSta")
process.tpPairsSta = process.tpPairs.clone(decay = "tagMuons@+ probeMuonsSta@-", cut = "2 < mass < 5")
process.onePairSta = cms.EDFilter("CandViewCountFilter", src = cms.InputTag("tpPairsSta"), minNumber = cms.uint32(1))

process.tpTreeSta = process.tpTree.clone(
    tagProbePairs = "tpPairsSta",
    variables = cms.PSet(
        KinematicVariables, 
        ## track matching variables
        tk_deltaR     = cms.InputTag("staToTkMatch","deltaR"),
        tk_deltaEta   = cms.InputTag("staToTkMatch","deltaEta"),
        tk_deltaR_NoJPsi     = cms.InputTag("staToTkMatchNoJPsi","deltaR"),
        tk_deltaEta_NoJPsi   = cms.InputTag("staToTkMatchNoJPsi","deltaEta"),
        tk_deltaR_NoBestJPsi     = cms.InputTag("staToTkMatchNoBestJPsi","deltaR"),
        tk_deltaEta_NoBestJPsi   = cms.InputTag("staToTkMatchNoBestJPsi","deltaEta"),
    ),
    flags = cms.PSet(
        outerValidHits = cms.string("outerTrack.numberOfValidHits > 0"),
        MuX_L2Mu0_L2   = LowPtTriggerFlagsEfficienciesProbe.MuX_L2Mu0_L2,
        TM  = cms.string("isTrackerMuon"),
        Glb = cms.string("isGlobalMuon"),
    ),
    tagVariables = cms.PSet(
        nVertices = cms.InputTag("nverticesModule"),
    ),
    tagFlags = cms.PSet(
        Mu0_L2Mu0_MU = LowPtTriggerFlagsEfficienciesTag.Mu0_L2Mu0_MU,
        Mu3_L2Mu0_MU = LowPtTriggerFlagsEfficienciesTag.Mu3_L2Mu0_MU,
        Mu5_L2Mu0_MU = LowPtTriggerFlagsEfficienciesTag.Mu5_L2Mu0_MU,
    ),
    pairVariables = cms.PSet(),
    pairFlags     = cms.PSet(),
    allProbes     = "probeMuonsSta",
    probeMatches  = "probeMuonsMCMatchSta",
)

process.tnpSimpleSequenceSta = cms.Sequence(
    process.tagMuons   * process.tagMuonsMCMatch   +
    process.oneTag     +
    process.probeMuonsSta * process.probeMuonsMCMatchSta +
    process.tpPairsSta      +
    process.onePairSta      +
    process.nverticesModule +
    process.staToTkMatchSequenceJPsi +
    process.tpTreeSta
)

process.tagAndProbeSta = cms.Path( 
    process.fastFilter +
    process.HLTMu      +
    process.muonsSta                       +
    process.patMuonsWithTriggerSequenceSta +
    process.tnpSimpleSequenceSta
)

process.TFileService = cms.Service("TFileService", fileName = cms.string("tnpJPsi_MC.root"))

# use this if you want to compute also 'unbiased' efficiencies, 
# - you have to remove all filters
# - you have to remove trigger requirements on the probes (but you can add a flag for them in the tree)
# note that it will be *much* slower and make a *much* bigger output tree!
if False:
    process.tagAndProbe.remove(process.oneTag)
    process.tagAndProbe.remove(process.onePair)
    process.tagAndProbe.remove(process.HLTBoth)
    process.tpTree.flags.TP_Probe_Cut = cms.string(process.probeMuons.cut.value())
    process.probeMuons.cut = "track.isNonnull"
    process.tpTree.makeMCUnbiasTree = True
if False:
    process.tagAndProbeSta.remove(process.oneTag)
    process.tagAndProbeSta.remove(process.onePairSta)
    process.tagAndProbeSta.remove(process.HLTMu)
    process.tpTreeSta.flags.TP_Probe_Cut = cms.string(process.probeMuonsSta.cut.value())
    process.probeMuonsSta.cut = "outerTrack.isNonnull"
    process.tpTreeSta.makeMCUnbiasTree = True