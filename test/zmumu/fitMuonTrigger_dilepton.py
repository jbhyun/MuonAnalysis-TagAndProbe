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
Syst = sys.argv[6]

print "#### Trigger Efficiency ####"
print "infile : "+infile
print "outfile : "+outfile
print "Trigger : "+PassingProbeTrigger
print "Period : "+Period
print "Systematic : "+Syst

N_Mass_Bin = 40
MassRange_Left = "70"
MassRange_Right = "130"
SignalShape = "vpv"
TagPt = 25
TagIso = 0.20
ProbeMultMax = 1

if Syst == "NMassBins30":
  N_Mass_Bin = 30
if Syst == "NMassBins50":
  N_Mass_Bin = 50
if Syst == "MassRange_60_130":
  MassRange_Left = "60"
  MassRange_Right = "130"
if Syst == "MassRange_70_120":
  MassRange_Left = "70"
  MassRange_Right = "120"
if Syst == "SignalShapeSingleV":
  SignalShape = "voigt"
if Syst == "TagPt30Iso0p08":
  TagPt = 30
  TagIso = 0.08
if Syst == "TagPt20IsoInf":
  TagPt = 20
  TagIso = 999
if Syst == "ProbeMult99":
  ProbeMultMax = 99

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
        mass   = cms.vstring("Tag-muon Mass", MassRange_Left, MassRange_Right, "GeV/c^{2}"),
        tag_pt = cms.vstring("tag muon p_{T}", "0", "1000", "GeV/c"),
        tag_combRelIsoPF04dBeta = cms.vstring("tag_combRelIsoPF04dBeta", "0", "0.1", ""),
        pt     = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
        abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
        pair_deltaR = cms.vstring("pair_deltaR", "0", "999", ""),
        dB = cms.vstring("dB", "0", "0.05", "cm"),
        dzPV = cms.vstring("dzPV", "-0.5", "0.5", "cm"),
        combRelIsoPF04dBeta = cms.vstring("combRelIsoPF04dBeta", "0", "0.1", ""),
        pair_probeMultiplicity = cms.vstring("pair_probeMultiplicity", "0", "99", ""),
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
                tag_pt = cms.vdouble(TagPt, 1000.),
                tag_combRelIsoPF04dBeta = cms.vdouble(0., TagIso),
                pair_probeMultiplicity = cms.vdouble(0., ProbeMultMax+0.5),
            ),
            BinToPDFmap = cms.vstring(
                SignalShape+"PlusExpo",
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
        vpvPlusExpoClosePeak = cms.vstring(
            "Voigtian::signal1(mass, mean1[91,89.1,120.1], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[91,89.1,120.1], width,        sigma2[4,1,10])",
            "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoClosePeakNarrow = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,85.1,110.1], width[2.495], sigma1[1,0.1,3])",
            "Voigtian::signal2(mass, mean2[90,88.1,110.1], width,        sigma2[3,1,5])",
            "SUM::signal(vFrac[0.8,0,1]*signal1, signal2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoPassFail = cms.vstring(
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
        vpvPlusExpoPassFail2 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,110.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,110.1], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.1,80.1,110.1], width[2.495], sigmaFail1[2, 0.1,6])",
            "Voigtian::signalFail2(mass, meanFail2[91.1,80.1,110.1], width,        sigmaFail2[2,   1,6])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoPassFail3 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,150.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,150.1], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.1,80.1,110.1], width[2.495], sigmaFail1[1.5,1,4])",
            "Voigtian::signalFail2(mass, meanFail2[91.1,80.1,110.1], width,        sigmaFail2[5,1,10])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoPassFail4 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,150.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,150.1], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[90.1,89.1,95.1], width[2.495], sigmaFail1[0.5,0.01,3])",
            "Voigtian::signalFail2(mass, meanFail2[90.1,89.1,95.1], width,        sigmaFail2[0.5,0.01,3])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoPassFail5 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,150.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,150.1], width,        sigmaPass2[5,1,10])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.1,80.1,120.1], width[2.495], sigmaFail1[1.5,1,4])",
            "Voigtian::signalFail2(mass, meanFail2[91.1,80.1,120.1], width,        sigmaFail2[1.5,1,4])",
            "SUM::signalFail(vFracFail[0.8,0.5,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusExpoPassFail6 = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,80.1,150.1], width[2.495], sigmaPass1[2.5,1,6])",
            "Voigtian::signalPass2(mass, meanPass2[91.1,80.1,150.1], width,        sigmaPass2[7,1,14])",
            "SUM::signalPass(vFracPass[0.8,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.1,80.1,150.1], width[2.495], sigmaFail1[2.5,1,6])",
            "Voigtian::signalFail2(mass, meanFail2[91.1,80.1,150.1], width,        sigmaFail2[7,1,14])",
            "SUM::signalFail(vFracFail[0.8,0,1]*signalFail1, signalFail2)",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),

        vpvPlusCheb_2nd = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,3,10])",
            "SUM::signal(vFrac[0.8,0.5,1]*signal1, signal2)",
            "RooChebychev::backgroundPass(mass, {ap0[0.2,-2.0,3.0], ap1[-0.1,-1.0,1.0], ap2[-0.1,-0.5,0.5]})",
            "RooChebychev::backgroundFail(mass, {af0[0.0,-3.0,2.0], af1[-0.2,-1.0,1.0], af2[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        vpvPlusCMS = cms.vstring(
            "Voigtian::signalPass1(mass, meanPass1[91.1,87,95], width[2.495], sigmaPass1[2.52,1.4,5.1])",
            "Voigtian::signalPass2(mass, meanPass2[91.2,87,95], width,        sigmaPass2[5.12,1.3,8.2])",
            "SUM::signalPass(vFracPass[0.7,0,1]*signalPass1, signalPass2)",
            "Voigtian::signalFail1(mass, meanFail1[91.3,87,100], width[2.495], sigmaFail1[2.4,1,5.3])",
            "Voigtian::signalFail2(mass, meanFail2[91.2,87,100], width,        sigmaFail2[5.2,1,10.1])",
            "SUM::signalFail(vFracFail[0.7,0,1]*signalFail1, signalFail2)",
            "RooCMSShape::backgroundPass(mass, alphaPass[60.,50.,80.], betaPass[0.021, 0.011,0.11], gammaPass[0.001, 0.,0.1], peakPass[90.01])",
            "RooCMSShape::backgroundFail(mass, alphaFail[90.,60.,150.], betaFail[0.05,0.01,0.2], gammaFail[2.0, 0.1,5.0], peakPass)",
            "efficiency[0.005,0.0001,0.01]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpo = cms.vstring(
            "Voigtian::signal(mass, mean[90,80,150], width[2.495], sigma[2,1,3])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoClosePeak = cms.vstring(
            "Voigtian::signal(mass, mean[90,86.1,150.1], width[2.495], sigma[2,1,3])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoClosePeakNarrow = cms.vstring(
            "Voigtian::signal(mass, mean[90,85.1,110.1], width[2.495], sigma[1,0.1,3])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,150.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[91.1,80.1,150.1], width[2.495], sigmaFail[2.5,1,6])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail2 = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,110.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[91.1,80.1,110.1], width[2.495], sigmaFail[2, 0.1,6])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail3 = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,150.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[91.1,80.1,110.1], width[2.495], sigmaFail[1.5,1,4])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail4 = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,150.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[90.1,89.1,95.1], width[2.495], sigmaFail[0.5,0.01,3])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail5 = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,150.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[91.1,80.1,120.1], width[2.495], sigmaFail[1.5,1,4])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusExpoPassFail6 = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,80.1,150.1], width[2.495], sigmaPass[2.5,1,6])",
            "Voigtian::signalFail(mass, meanFail[91.1,80.1,150.1], width[2.495], sigmaFail[2.5,1,6])",
            "Exponential::backgroundPass(mass, lp[-0.1,-1,0.1])",
            "Exponential::backgroundFail(mass, lf[-0.1,-1,0.1])",
            "efficiency[0.9,0,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusCheb_2nd = cms.vstring(
            "Voigtian::signal(mass, mean[90,80,100], width[2.495], sigma[2,1,3])",
            "RooChebychev::backgroundPass(mass, {ap0[0.2,-2.0,3.0], ap1[-0.1,-1.0,1.0], ap2[-0.1,-0.5,0.5]})",
            "RooChebychev::backgroundFail(mass, {af0[0.0,-3.0,2.0], af1[-0.2,-1.0,1.0], af2[0.0,-0.5,0.5]})",
            "efficiency[0.9,0.7,1]",
            "signalFractionInPassing[0.9]"
        ),
        voigtPlusCMS = cms.vstring(
            "Voigtian::signalPass(mass, meanPass[91.1,87,95], width[2.495], sigmaPass[2.52,1.4,5.1])",
            "Voigtian::signalFail(mass, meanFail[91.3,87,100], width[2.495], sigmaFail[2.4,1,5.3])",
            "RooCMSShape::backgroundPass(mass, alphaPass[60.,50.,80.], betaPass[0.021, 0.011,0.11], gammaPass[0.001, 0.,0.1], peakPass[90.01])",
            "RooCMSShape::backgroundFail(mass, alphaFail[90.,60.,150.], betaFail[0.05,0.01,0.2], gammaFail[2.0, 0.1,5.0], peakPass)",
            "efficiency[0.005,0.0001,0.01]",
            "signalFractionInPassing[0.9]"
        ),
    ),
    ## How to do the fit
    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(N_Mass_Bin),
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
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin10*", SignalShape+"PlusExpo",
        "*abseta_bin1*pt_bin11*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail", # PlusExpo->PlusExpoPassFail (DONE)
        "*abseta_bin1*pt_bin9*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin11*", SignalShape+"PlusExpo",
        "*abseta_bin2*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin2*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin3*", SignalShape+"PlusExpo", # [DONE] PlusExo(good, but try)->PlusExpoPassFail(worse, go back)->PlusExo
        "*abseta_bin1*pt_bin4*", SignalShape+"PlusExpoPassFail4", # PlusExpoPassFail->PlusExpo->PlusCheb_2nd->PlusExpoClosePeak->PlusExpoClosePeakNarrow->PlusExpoPassFail4
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin2*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin4*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin11*", SignalShape+"PlusExpoPassFail",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin11*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin3*", SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin11*", SignalShape+"PlusExpoPassFail5",# [DONE] PlusExpo->PlusExpoPassFail->PlusExpoPassFail3->PlusExpoPassFail4->PlusExpoPassFail5
        "*abseta_bin3*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin11*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        #"*abseta_bin0*pt_bin1*", SignalShape+"PlusCMS", # [DONE] PlusExpoPassFail->PlusExpo->PlusCheb_2nd->PlusExpoClosePeak->PlusExpoPassFail4(better.. but try)->PlusCMS
        "*abseta_bin0*pt_bin2*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin7*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin8*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin9*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin11*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin10*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin11*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin1;*", SignalShape+"PlusCMS", # [DONE] PlusExpoPassFail->PlusExpo->PlusCheb_2nd->PlusExpoClosePeak->PlusExpoPassFail4(better.. but try)->PlusCMS
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
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpo",# [DONE] PlusExpoPassFail->PlusExpo
        "*abseta_bin2*pt_bin6*", SignalShape+"PlusExpoPassFail",# [DONE] PlusExpo(okay... but try)->PlusExpoPassFail
        "*abseta_bin3*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin1*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",

      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail2", # PlusExpo->PlusExpoPassFail->PlusExpoPassFail2
        "*abseta_bin1*pt_bin1*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin6*", SignalShape+"PlusExpoPassFail",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpo",# [DONE] PlusExpoPassFail(okay,, but try)->PlusExpo
        "*abseta_bin2*pt_bin6*", SignalShape+"PlusExpoPassFail3",# [DONE] PlusExpo(okay,,, but try)->PlusExpoPassFail(error)->PlusExpoPassFail3
        "*abseta_bin3*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin1*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpo", # [DONE] PlusExpoPassFail->PlusExpo(good, but try)->PlusCheb_2nd->PlusExpo
        "*abseta_bin0*pt_bin1*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin2*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin1*", SignalShape+"PlusExpo",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin6*", SignalShape+"PlusExpoPassFail",
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


#######################################################
#
#
if PassingProbeTrigger=="Mu23_TrkIsoVVL":
  process.TnP_Muon_Trigger.Categories.Mu23_TrkIsoVVL = cms.vstring("Mu23_TrkIsoVVL", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("Mu23_TrkIsoVVL", "pass")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinnedVariables.pt = cms.vdouble(10, 15, 20, 21, 22, 23, 24, 25, 30, 40, 50, 60, 120)

  if Period=="BCDEF":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin11*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin11*", SignalShape+"PlusExpoPassFail",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin1*pt_bin11*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
      )
#
#
#########################################################

#######################################################
#
#
if PassingProbeTrigger=="IsoMu24_OR_IsoTkMu24":
  process.TnP_Muon_Trigger.Categories = cms.PSet(
    IsoMu24   = cms.vstring("IsoMu24", "dummy[pass=1,fail=0]"),
    IsoTkMu24 = cms.vstring("IsoTkMu24", "dummy[pass=1,fail=0]"),
  )
  process.TnP_Muon_Trigger.Expressions = cms.PSet(
    Exp_IsoMu24_OR_IsoTkMu24 = cms.vstring("Exp_IsoMu24_OR_IsoTkMu24", "IsoMu24==1 || IsoTkMu24==1", "IsoMu24", "IsoTkMu24")
  )
  process.TnP_Muon_Trigger.Cuts.IsoMu24_OR_IsoTkMu24 = cms.vstring("IsoMu24_OR_IsoTkMu24", "Exp_IsoMu24_OR_IsoTkMu24", "0.5")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("IsoMu24_OR_IsoTkMu24", "above")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinnedVariables.pt = cms.vdouble(10, 15, 20, 22, 24, 25, 26, 28, 30, 40, 50, 60, 120)

  if Period=="BCDEF":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin1*pt_bin9*", SignalShape+"PlusExpoPassFail",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin9*", SignalShape+"PlusExpoPassFail4",
        "*abseta_bin1*pt_bin10*", SignalShape+"PlusExpoPassFail6",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin9*", SignalShape+"PlusExpoPassFail4",
      )
#
#
#########################################################

#######################################################
#
#
if PassingProbeTrigger=="Mu8":

  process.TnP_Muon_Trigger.Categories.DoubleIsoMu17Mu8_IsoMu8leg = cms.vstring("DoubleIsoMu17Mu8_IsoMu8leg", "dummy[pass=1,fail=0]")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.EfficiencyCategoryAndState = cms.vstring("DoubleIsoMu17Mu8_IsoMu8leg", "pass")

  if Period=="BCDEF":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpo", ##
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpo",
        "*abseta_bin2*pt_bin6*", SignalShape+"PlusExpo", ##
        "*abseta_bin3*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin1*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",

      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail2",
        "*abseta_bin1*pt_bin1*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin5*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin6*", SignalShape+"PlusExpoPassFail",
      )
  if Period=="GH":
    if "MC" in infile:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin3*", SignalShape+"PlusExpoPassFail", ##
        "*abseta_bin1*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpo",
        "*abseta_bin2*pt_bin6*", SignalShape+"PlusExpo", ##
        "*abseta_bin3*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpo",
        "*abseta_bin3*pt_bin1*", SignalShape+"PlusExpo", ##
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
      )
    else:
      process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_Trigger_pt_eta.BinToPDFmap = cms.vstring(
        SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpo",
        "*abseta_bin0*pt_bin1*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin2*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin4*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin0*pt_bin6*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin0*tag_pt_bin0*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin1*pt_bin1*", SignalShape+"PlusExpo",
        "*abseta_bin2*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin3*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin5*", SignalShape+"PlusExpoPassFail",
        "*abseta_bin3*pt_bin6*", SignalShape+"PlusExpoPassFail",
      )
#
#
#########################################################










process.p1 = cms.Path(process.TnP_Muon_Trigger)
