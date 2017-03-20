import FWCore.ParameterSet.Config as cms

process = cms.Process("TagProbe")

process.load('FWCore.MessageService.MessageLogger_cfi')
process.source = cms.Source("EmptySource")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )

process.TnP_Muon_ID = cms.EDAnalyzer("TagProbeFitTreeAnalyzer",
    ## Input, output 
    InputFileNames = cms.vstring(
      'file:/data4/Users/jskim/TagAndProbe/tree/TnPTree_80XRereco_Run2016GH_dXYSIG_ADDED_SKIMMED.root'
    ),
    OutputFileName = cms.string(
      "/data4/Users/jskim/TagAndProbe/results/TnP_Muon_ID_Data.root"
    ),
    InputTreeName = cms.string("fitter_tree"), 
    InputDirectoryName = cms.string("tpTree"),  
    ## Variables for binning
    Variables = cms.PSet(
        mass   = cms.vstring("Tag-muon Mass", "70", "130", "GeV/c^{2}"),
        pt     = cms.vstring("muon p_{T}", "0", "1000", "GeV/c"),
        #eta = cms.vstring("muon #eta", "-2.5", "2.5", ""),
        abseta = cms.vstring("muon |#eta|", "0", "2.5", ""),
        dB     = cms.vstring("dB", "0", "9999", "cm"),
        dXYSig = cms.vstring("dXYSig", "0", "9999", ""),
        dzPV   = cms.vstring("dzPV", "-9999", "9999", "cm"),
        combRelIsoPF04dBeta = cms.vstring("pf relative isolation", "0", "999", ""),

    ),
    ## Flags you want to use to define numerator and possibly denominator
    Categories = cms.PSet(
        Tight2012 = cms.vstring("Tight2012", "dummy[pass=1,fail=0]"),
    ),
    ## Cuts: name, variable, cut threshold    
    Cuts = cms.PSet(
        ## dZ is missing in Tight2012 ##
        dZMin = cms.vstring("dZMin", "dzPV", "-0.5"),
        dZMax = cms.vstring("dZMax", "dzPV", "0.5"),
        ## HN Tight ##
        PFIsoTight = cms.vstring("PFIsoTight" ,"combRelIsoPF04dBeta", "0.1"),
        dBTight = cms.vstring("dBTight", "dB", "0.05"),
        dXYSigSmall = cms.vstring("dXYSigSmall", "dXYSig", "3.0"),
    ),
    ## What to fit
    Efficiencies = cms.PSet(
        HN_TRI_TIGHT_pt_eta = cms.PSet(
            #### Skimming ####
            #### 1. Tag pT > 25.9999 GeV
            #### 2. Tag RelIso04 < 0.2
            #### 3. Tag IsoMu24 trigger
            #### 4. Probe pT > 4.9999 GeV
            #### 5. pair_probeMultiplicity = 1
            UnbinnedVariables = cms.vstring("mass"),
            EfficiencyCategoryAndState = cms.vstring(
                ## POG Tight ##
                "Tight2012", "pass",
                "dZMin", "above",
                "dZMax", "below",
                ## HN Tight ##
                "PFIsoTight", "below",
                "dBTight", "below",
                "dXYSigSmall", "below",
            ), ## Numerator definition
            BinnedVariables = cms.PSet(
                ## Binning in continuous variables
                abseta = cms.vdouble( 0.0, 0.8, 1.479, 2.0, 2.5 ),
                pt     = cms.vdouble( 10., 20., 25., 30., 35., 45., 60., 80., 100., 200. ),
                ## flags and conditions required at the denominator, 
            ),
            BinToPDFmap = cms.vstring(
                "vpvPlusExpo",
                "*eta_bin0*pt_bin0*", "vpvPlusExpo",
                "*eta_bin0*pt_bin1*", "vpvPlusExpo",
                "*eta_bin0*pt_bin2*", "vpvPlusExpo",
                "*eta_bin0*pt_bin3*", "vpvPlusCheb",
                "*eta_bin0*pt_bin4*", "vpvPlusCheb",
                "*eta_bin0*pt_bin5*", "vpvPlusCheb",
                "*eta_bin0*pt_bin6*", "vpvPlusCheb",
                "*eta_bin0*pt_bin7*", "vpvPlusCheb",
                "*eta_bin0*pt_bin8*", "vpvPlusCheb",
                "*eta_bin1*pt_bin0*", "vpvPlusExpo",
                "*eta_bin1*pt_bin1*", "vpvPlusExpo",
                "*eta_bin1*pt_bin2*", "vpvPlusExpo",
                "*eta_bin1*pt_bin3*", "vpvPlusCheb",
                "*eta_bin1*pt_bin4*", "vpvPlusCheb",
                "*eta_bin1*pt_bin5*", "vpvPlusCheb",
                "*eta_bin1*pt_bin6*", "vpvPlusCheb",
                "*eta_bin1*pt_bin7*", "vpvPlusCheb",
                "*eta_bin1*pt_bin8*", "vpvPlusCheb",
                "*eta_bin2*pt_bin0*", "vpvPlusExpo",
                "*eta_bin2*pt_bin1*", "vpvPlusCheb",
                "*eta_bin2*pt_bin2*", "vpvPlusCheb",
                "*eta_bin2*pt_bin3*", "vpvPlusExpo",
                "*eta_bin2*pt_bin4*", "vpvPlusCheb",
                "*eta_bin2*pt_bin5*", "vpvPlusCheb",
                "*eta_bin2*pt_bin6*", "vpvPlusCMSbeta0p2",
                "*eta_bin2*pt_bin7*", "vpvPlusCheb",
                "*eta_bin2*pt_bin8*", "vpvPlusCMSbeta0p2",
                "*eta_bin3*pt_bin0*", "vpvPlusExpo",
                "*eta_bin3*pt_bin1*", "vpvPlusExpo",
                "*eta_bin3*pt_bin2*", "vpvPlusExpo",
                "*eta_bin3*pt_bin3*", "vpvPlusCheb",
                "*eta_bin3*pt_bin4*", "vpvPlusCheb",
                "*eta_bin3*pt_bin5*", "vpvPlusCheb",
                "*eta_bin3*pt_bin6*", "vpvPlusCheb",
                "*eta_bin3*pt_bin7*", "vpvPlusCheb",
                "*eta_bin3*pt_bin8*", "vpvPlusCheb",
            ), 


        )
    ),
    ## PDF for signal and background (double voigtian + exponential background)
    PDFs = cms.PSet(
        vpvPlusExpo = cms.vstring(
            "Voigtian::signal1(mass, mean1[90,80,100], width[2.495], sigma1[2,1,3])",
            "Voigtian::signal2(mass, mean2[90,80,100], width,        sigma2[4,2,10])",
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

    ),
    ## How to do the fit
    binnedFit = cms.bool(True),
    binsForFit = cms.uint32(40),
    saveDistributionsPlot = cms.bool(False),
    NumCPU = cms.uint32(1), ## leave to 1 for now, RooFit gives funny results otherwise
    SaveWorkspace = cms.bool(False),
)

process.p1 = cms.Path(process.TnP_Muon_ID)
