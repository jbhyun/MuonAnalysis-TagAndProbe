
#include "FWCore/Framework/interface/MakerMacros.h"

#include "MuonAnalysis/TagAndProbe/interface/TagProbeProducer.h"
#include "MuonAnalysis/TagAndProbe/interface/MatchedProbeMaker.h"
#include "MuonAnalysis/TagAndProbe/interface/TagProbeAnalyzer.h"
#include "MuonAnalysis/TagAndProbe/interface/Histogrammer.h"

DEFINE_ANOTHER_FWK_MODULE(TagProbeProducer);
DEFINE_ANOTHER_FWK_MODULE(MatchedProbeMaker);
DEFINE_ANOTHER_FWK_MODULE(TagProbeAnalyzer);
DEFINE_ANOTHER_FWK_MODULE(Histogrammer);