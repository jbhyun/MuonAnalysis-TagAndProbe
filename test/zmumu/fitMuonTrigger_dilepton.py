import os
import FWCore.ParameterSet.Config as cms

### USAGE:
###    cmsRun fitMuonTrigger_trilepton <input> <output>
###    ex> cmsRun TriggerEff.py mc IsoMu20_from_Tight2012
### scenarios:
###   - data_all (default)  
###   - signal_mc

import sys
infile = sys.argv[2]  
outfile = sys.argv[3]
PassingProbeTrigger = sys.argv[4]
Period = sys.argv[5]

print "#### Trigger Efficiency ####"
print "infile : "+infile
print "outfile : "+outfile
print "Trigger : "+PassingProbeTrigger
print "Period : "+Period

process = cms.Process("TagProbe")

process.load('FWCore.MessageService.MessageLogger_cfi')
process.source = cms.Source("EmptySource")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.TnP_Muon_Trigger = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",

    ## Input, output 
    InputFileNames = cms.vstring(
      infile
    ),
    OutputFileName = cms.string(
      outfile
    ),
    InputTreeName = cms.string("fitter_tree"), 
    InputDirectoryName = cms.string("tpTree"),  

    ## Variables for binning
    Variables = cms.PSet(
        mass   = cms.vstring("Tag-muon Mass", "70", "130", "GeV/c^{2}"),
        pt     = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
        abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
        pair_deltaR = cms.vstring("pair_deltaR", "0", "999", ""),
        dB = cms.vstring("dB", "0", "0.05", "cm"),
        dzPV = cms.vstring("dzPV", "-0.5", "0.5", "cm"),
        combRelIsoPF04dBeta = cms.vstring("combRelIsoPF04dBeta", "0", "0.1", ""),
    ),

    ## Flags you want to use to define numerator and possibly denominator
    Categories = cms.PSet(
        #e.g., DoubleIsoMu17Mu8_IsoMu17leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu17leg", "dummy[pass=1,fail=0]"),
    ),

    ## Cuts: name, variable, cut threshold
    ## can be used only for passing probes
    Cuts = cms.PSet(
    ),

    Expressions = cms.PSet(
    ),

    ## What to fit
    Efficiencies = cms.PSet(
        HN_TRI_TIGHT_Trigger_pt_eta = cms.PSet(
            #### Skimming ####
            #### 1. Tag pT > 25.9999 GeV
            #### 2. Tag RelIso04 < 0.2
            #### 3. Tag IsoMu24 trigger
            #### 4. Probe pT > 9.9999 GeV
            #### 5. pair_probeMultiplicity = 1
            #### below, HN Trilep Tight ID
            #### 6. Tight2012
            #### 7. dzPV > -0.5
            #### 8. dzPV < 0.5
            #### 9. combRelIsoPF04dBeta < 0.1
            #### 10. dB < 0.05 
            #### 11. dXYSig < 3.0
            UnbinnedVariables = cms.vstring("mass"),
            EfficiencyCategoryAndState = cms.vstring(
                #e.g., "DoubleIsoMu17Mu8_IsoMu17leg", "pass"
            ), ## Numerator definition
            BinnedVariables = cms.PSet(
                ## Binning in continuous variables
                pt = cms.vdouble(10, 20, 25, 30, 40, 50, 60, 120),
                abseta = cms.vdouble(0., 0.9, 1.2, 2.1, 2.4),
                pair_deltaR = cms.vdouble(0.3, 999),
                dB = cms.vdouble(0., 0.005),
                dzPV = cms.vdouble(-0.04, 0.04),
                combRelIsoPF04dBeta = cms.vdouble(0., 0.07),
                ## flags and conditions required at the denominator, 
            ),
            BinToPDFmap = cms.vstring(
                "vpvPlusExpo",
            ), 


        )
    ),
    ## PDF for signal and background (double voigtian + exponential background)
    PDFs = cms.PSet(
        vpvPlusExpo = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,150], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,150], width,        sigma2[4,2,10])",
            "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCMSbeta0p2 = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "RooCMSShape::backgroundPass(mass, alphaPass[70.,60.,90.], betaPass[0.001, 0.,0.1], gammaPass[0.001, 0.,0.1], peakPass[90.0])",
            "RooCMSShape::backgroundFail(mass, alphaFail[70.,60.,90.], betaFail[0.03, 0.02,0.1], gammaFail[0.001, 0.,0.1], peakPass)",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCheb_2nd = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "RooChebychev::backgroundPass(mass, {ap0[-0.5,-3.0,2.0], ap1[0.1,-1.0,1.0], ap2[0.1,-0.5,0.5] })",
            "RooChebychev::backgroundFail(mass, {af0[-1.0,-3.0,2.0], af1[0.1,-1.0,1.0], af2[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCheb_3rd = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "RooChebychev::backgroundPass(mass, {ap0[0.2,-2.0,3.0], ap1[-0.1,-1.0,1.0], ap2[-0.1,-0.5,0.5], ap3[0.0,-0.5,0.5]})",
            "RooChebychev::backgroundFail(mass, {af0[0.0,-3.0,2.0], af1[-0.2,-1.0,1.0], af2[0.0,-0.5,0.5],  af3[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCheb_4th = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "RooChebychev::backgroundPass(mass, {ap0[0.2,-2.0,3.0], ap1[-0.1,-1.0,1.0], ap2[-0.1,-0.5,0.5], ap3[0.0,-0.5,0.5], ap4[0.0,-0.5,0.5]})",
            "RooChebychev::backgroundFail(mass, {af0[0.0,-3.0,2.0], af1[-0.2,-1.0,1.0], af2[0.0,-0.5,0.5],  af3[0.0,-0.5,0.5], af4[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCheb = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "RooChebychev::backgroundPass(mass, {ap0[0.2,-2.0,3.0], ap1[-0.1,-1.0,1.0], ap2[-0.1,-0.5,0.5], ap3[0.0,-0.5,0.5], ap4[0.0,-0.5,0.5], ap5[0.0,-0.5,0.5]})",
            "RooChebychev::backgroundFail(mass, {af0[0.0,-3.0,2.0], af1[-0.2,-1.0,1.0], af2[0.0,-0.5,0.5],  af3[0.0,-0.5,0.5], af4[0.0,-0.5,0.5], af5[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpo3 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,150.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,150.1], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.1,80.1,150.1], width[2.495], sigmaFail1[2.5,1,6])",
            "Voigtian::signalFail2(mass, meanFail2[91.1,80.1,150.1], width,        sigmaFail2[5,1,10])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),

    ),
    ## How to do the fit
    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(40),
    saveDistributionsPlot = cms.bool(False),
    NumCPU = cms.uint32(1), ## leave to 1 for now, RooFit gives funny results otherwise
    SaveWorkspace = cms.bool(False),
)

if "MC" in infile:
  print "This is MC"
  if Period=="BCDEF":
    print "  reweighting w.r.t BCDEF"
    process.TnP_Muon_Trigger.Variables.weight_BtoF = cms.vstring("weight_BtoF","-10000","10000","")
    process.TnP_Muon_Trigger.WeightVariable = cms.string("weight_BtoF")
    process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.UnbinnedVariables = cms.vstring("mass", "weight_BtoF")
  if Period=="GH":
    print "  reweighting w.r.t GH"
    process.TnP_Muon_Trigger.Variables.weight_GtoH = cms.vstring("weight_GtoH","-10000","10000","")
    process.TnP_Muon_Trigger.WeightVariable = cms.string("weight_GtoH")
    process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.UnbinnedVariables = cms.vstring("mass", "weight_GtoH")

if Period=="BCDEF":
  print "BCDEF period => applying dPhi cut"
  process.TnP_Muon_Trigger.Variables.pair_dPhiPrimeDeg = cms.vstring("#delta#phi(tag, probe)", "0", "9999", "")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinnedVariables.pair_dPhiPrimeDeg = cms.vdouble( 70, 9999 )

#######################################################
#
#
if PassingProbeTrigger=="DoubleIsoMu17Mu8_IsoMu17leg":
  process.TnP_Muon_Trigger.Categories.DoubleIsoMu17Mu8_IsoMu17leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu17leg", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu17leg", "pass") 
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinnedVariables.pt = cms.vdouble(10, 15, 16, 17, 18, 19, 20, 25, 30, 40, 50, 60, 120)

  if Period=="BCDEF":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin1*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin9*", "vpvPlusExpo3", # 2nd try
        "*abseta_bin0*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin10*", "vpvPlusExpo",
        "*abseta_bin2*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin11*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin11*", "vpvPlusExpo", # 2nd try
        "*abseta_bin3*pt_bin11*", "vpvPlusCheb_3rd",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin1_*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin2*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin2*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin2*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin3*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin4*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin11*", "vpvPlusExpo3",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin3*", "vpvPlusExpo",
        "*abseta_bin1*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin3*", "vpvPlusExpo",
        "*abseta_bin*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin11*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin11*", "vpvPlusCheb_3rd",
        "*abseta_bin2*pt_bin10*", "vpvPlusCheb_3rd",
        "*abseta_bin2*pt_bin11*", "vpvPlusCheb_4th",
        "*abseta_bin3*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin11*", "vpvPlusExpo3",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin1_*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin2*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin10*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin11*", "vpvPlusExpo3",
      )

#
#
#######################################################




if PassingProbeTrigger=="DoubleIsoMu17Mu8_IsoMu8leg":
  process.TnP_Muon_Trigger.Categories.DoubleIsoMu17Mu8_IsoMu8leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu8leg", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu8leg", "pass")

if PassingProbeTrigger=="DoubleIsoMu17TkMu8_IsoMu17leg":
  process.TnP_Muon_Trigger.Categories.DoubleIsoMu17TkMu8_IsoMu17leg = cms.vstring("DoubleIsoMu17TkMu8_IsoMu17leg", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17TkMu8_IsoMu17leg", "pass")

if PassingProbeTrigger=="DoubleIsoMu17TkMu8_IsoMu8leg":
  process.TnP_Muon_Trigger.Categories.DoubleIsoMu17TkMu8_IsoMu8leg = cms.vstring("DoubleIsoMu17TkMu8_IsoMu8leg", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17TkMu8_IsoMu8leg", "pass")






#######################################################
#
#
if PassingProbeTrigger=="Mu8_OR_TkMu8":
  process.TnP_Muon_Trigger.Categories = cms.PSet(
    DoubleIsoMu17Mu8_IsoMu8leg   = cms.vstring("DoubleIsoMu17Mu8_IsoMu8leg", "dummy[pass=1,fail=0]"),
    DoubleIsoMu17TkMu8_IsoMu8leg = cms.vstring("DoubleIsoMu17TkMu8_IsoMu8leg", "dummy[pass=1,fail=0]"),
  )
  process.TnP_Muon_Trigger.Expressions = cms.PSet(
    Exp_Mu8_OR_TkMu8 = cms.vstring("Exp_Mu8_OR_TkMu8", "DoubleIsoMu17Mu8_IsoMu8leg==1 || DoubleIsoMu17TkMu8_IsoMu8leg==1", "DoubleIsoMu17Mu8_IsoMu8leg", "DoubleIsoMu17TkMu8_IsoMu8leg")
  )
  process.TnP_Muon_Trigger.Cuts.Mu8_OR_TkMu8 = cms.vstring("Mu8_OR_TkMu8", "Exp_Mu8_OR_TkMu8", "0.5")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("Mu8_OR_TkMu8", "above")

  if Period=="BCDEF":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin6*", "vpvPlusExpo", # 2nd try
        "*abseta_bin3*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin1*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin6*", "vpvPlusCheb_3rd",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin0*", "vpvPlusExpo",
        "*abseta_bin1*pt_bin1*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin6*", "vpvPlusExpo3",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin0*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin6*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin4*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin2*pt_bin6*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin0*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin1*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin6*", "vpvPlusCheb_3rd",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        "vpvPlusExpo",
        "*abseta_bin0*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin0*", "vpvPlusExpo3",
        "*abseta_bin1*pt_bin1*", "vpvPlusExpo",
        "*abseta_bin3*pt_bin3*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin5*", "vpvPlusExpo3",
        "*abseta_bin3*pt_bin6*", "vpvPlusExpo3",
      )
#
#
#########################################################


if PassingProbeTrigger=="test1":
  process.TnP_Muon_Trigger.Categories = cms.PSet(
      DoubleIsoMu17Mu8_IsoMu17leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu17leg", "dummy[pass=1,fail=0]"),
      DoubleIsoMu17TkMu8_IsoMu17leg = cms.vstring("DoubleIsoMu17TkMu8_IsoMu17leg", "dummy[pass=1,fail=0]"),
  )
  process.TnP_Muon_Trigger.Expressions.Exp_test1 = cms.vstring(
      "Exp_test1", 
      "DoubleIsoMu17Mu8_IsoMu17leg==1 && DoubleIsoMu17TkMu8_IsoMu17leg!=1", 
      "DoubleIsoMu17Mu8_IsoMu17leg", "DoubleIsoMu17TkMu8_IsoMu17leg"
  )
  process.TnP_Muon_Trigger.Cuts.test1 = cms.vstring("test1", "Exp_test1", "0.5")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("test1", "above")

process.p1 = cms.Path(process.TnP_Muon_Trigger)
