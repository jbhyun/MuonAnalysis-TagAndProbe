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
Period = sys.argv[4]

print "#### Trigger Efficiency ####"
print "infile : "+infile
print "outfile : "+outfile
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
        tag_abseta = cms.vstring("tag muon |#eta|", "0.", "2.5", ""),
        abseta = cms.vstring("probe muon |#eta|", "0.", "2.5", ""),
        pair_deltaR = cms.vstring("pair_deltaR", "0", "999", ""),
        tag_pt = cms.vstring("tag_pt", "0", "99999", "GeV/c"),
    ),

    ## Flags you want to use to define numerator and possibly denominator
    Categories = cms.PSet(
        PassDZTrigger = cms.vstring("PassDZTrigger", "dummy[pass=1,fail=0]"),
    ),

    ## Cuts: name, variable, cut threshold
    ## can be used only for passing probes
    Cuts = cms.PSet(
    ),

    ## What to fit
    Efficiencies = cms.PSet(
        HN_TRI_TIGHT_TriggerDZFilter_tag_eta_eta = cms.PSet(
            UnbinnedVariables = cms.vstring("mass"),
            EfficiencyCategoryAndState = cms.vstring(
              "PassDZTrigger", "pass",
            ), ## Numerator definition
            BinnedVariables = cms.PSet(
                ## Binning in continuous variables
                #tag_eta = cms.vdouble(-2.4, -2.0, -1.5, -1.0, -0.5, 0., 0.5, 1.0, 1.5, 2.0, 2.4),
                #eta = cms.vdouble(-2.4, -2.0, -1.5, -1.0, -0.5, 0., 0.5, 1.0, 1.5, 2.0, 2.4),
                tag_abseta = cms.vdouble(0., 0.9, 1.2, 2.1, 2.4),
                abseta = cms.vdouble(0., 0.9, 1.2, 2.1, 2.4),
                pair_deltaR = cms.vdouble(0.3, 999),
                tag_pt = cms.vdouble(19.9999,99999),
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
    process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_TriggerDZFilter_tag_eta_eta.UnbinnedVariables = cms.vstring("mass", "weight_BtoF")
  if Period=="GH":
    print "  reweighting w.r.t GH"
    process.TnP_Muon_Trigger.Variables.weight_GtoH = cms.vstring("weight_GtoH","-10000","10000","")
    process.TnP_Muon_Trigger.WeightVariable = cms.string("weight_GtoH")
    process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_TriggerDZFilter_tag_eta_eta.UnbinnedVariables = cms.vstring("mass", "weight_GtoH")

if Period=="BCDEF":
  print "BCDEF period => applying dPhi cut"
  process.TnP_Muon_Trigger.Variables.pair_dPhiPrimeDeg = cms.vstring("#delta#phi(tag, probe)", "0", "9999", "")
  process.TnP_Muon_Trigger.Efficiencies.HN_TRI_TIGHT_TriggerDZFilter_tag_eta_eta.BinnedVariables.pair_dPhiPrimeDeg = cms.vdouble( 70, 9999 )





process.p1 = cms.Path(process.TnP_Muon_Trigger)
