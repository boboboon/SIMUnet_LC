/**
 * lhcb-wz
 *
 * W and Z production data from the LHCb experiment
 *
 * Final data from the LHCb paper: 1204.1620
 *
 * Full experimental correlation matrix provided
 * with the measurement
 *
 * Luminosity uncertainty is about a constant 3.4% in
 * all data points
 *
 */

#include "LHCb.h"

void LHCBW36PBFilter::ReadData()
{
  cout << "**** LHCBW36PB Warning - Z Results not filtered ****"<<endl;
  // Opening files
  fstream f1, f2, f3, f4;

  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/lhcb_36pb_wplrap.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream datafile2("");
  datafile2 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_36pb_wmlrap.data";
  f2.open(datafile2.str().c_str(), ios::in);

  if (f2.fail()) {
    cerr << "Error opening data file " << datafile2.str() << endl;
    exit(-1);
  }

  stringstream datafile3("");
  datafile3 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_36pb_zrap.data";
  f3.open(datafile3.str().c_str(), ios::in);

  if (f3.fail()) {
    cerr << "Error opening data file " << datafile3.str() << endl;
    exit(-1);
  }

  stringstream datafile4("");
  datafile4 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_36pb_covmat.data";
  f4.open(datafile4.str().c_str(), ios::in);

  if (f4.fail()) {
    cerr << "Error opening data file " << datafile4.str() << endl;
    exit(-1);
  }

  // Starting filter
  const int ndata_wp = 5;
  const int ndata_wm = 5;
  //const int ndata_z = 5;
  const double convfac = 1000.; // Must multiply from pb to fb
  double MW2 = pow(MW,2.0);
  //double MZ2 = pow(fSettings.GetMZ(),2.0);
  double s = 7000;
  string line;

  double totsys[fNData];
  double etamin, etamax;
  int idat = 0;

  cout << "********** WARNING: Converting pb to fb to match ApplGrid output ********" << endl;

  // W+
  for (int i = 0; i < ndata_wp; i++)
  {
    getline(f1,line);
    istringstream lstream(line);

    lstream >> etamin >> etamax;
    fKin1[idat+i] = (etamax + etamin)*0.5;     //eta
    fKin2[idat+i] = MW2;                       //mass W squared
    fKin3[idat+i] = s;                         //sqrt(s)

    lstream >> fData[idat+i];
    fData[idat+i] *= convfac;
    lstream >> fStat[idat+i];
    fStat[idat+i] *= convfac;
    lstream >> totsys[idat+i];
    totsys[idat+i] *= convfac;

    fSys[idat+i][0].mult = 3.5;                     //luminosity uncertainty of 3.5%
    fSys[idat+i][0].add = fSys[idat+i][0].mult*fData[i]*1e-2;
    fSys[idat+i][0].type = MULT;
    fSys[idat+i][0].name = "CORR";
  }
  idat+=ndata_wp;
  // W-
  for (int i = 0; i < ndata_wm; i++)
  {
    getline(f2,line);
    istringstream lstream(line);

    lstream >> etamin >> etamax;
    fKin1[idat+i] = (etamax + etamin)*0.5;     //eta
    fKin2[idat+i] = MW2;                       //mass W squared
    fKin3[idat+i] = s;                         //sqrt(s)

    lstream >> fData[idat+i];
    fData[idat+i] *= convfac;
    lstream >> fStat[idat+i];
    fStat[idat+i] *= convfac;
    lstream >> totsys[idat+i];
    totsys[idat+i] *= convfac;

    fSys[idat+i][0].mult = 3.5;                     //luminosity uncertainty of 3.5%
    fSys[idat+i][0].add = fSys[idat+i][0].mult*fData[i]*1e-2;
    fSys[idat+i][0].type = MULT;
    fSys[idat+i][0].name = "CORR";
  }
  idat+=ndata_wm;
/*  Z data not used
  // Z
  for (int i = 0; i < ndata_Z; i++)
  {
    getline(f3,line);
    istringstream lstream(line);

    lstream >> etamin >> etamax;
    fKin1[idat+i] = (etamax + etamin)*0.5;     //eta
    fKin2[idat+i] = MZ2;                       //mass W squared
    fKin3[idat+i] = s;                         //sqrt(s)

    lstream >> fData[idat+i];
    lstream >> fStat[idat+i];
    lstream >> totsys[idat+i];

    fSys[idat+i][0].mult = 3.5;                     //luminosity uncertainty of 3.5%
    fSys[idat+i][0].add = fSys[idat+i][0].mult*fData[i]*1e-2;
    fSys[idat+i][0].type = MULT;
    fSys[idat+i][0].name = "CORR";
  }
*/

  //Reading correlation matrix
  //Format of table means we need to read all 15 points (W+,W- and Z)
  double inmat[15][15];
  for (int i = 0; i < 15; i++)
  {
    getline(f4,line);
    istringstream lstream(line);
    for (int j = 0; j < i+1; j++)      //Only lower diagonal in file
    {
      lstream >> inmat[i][j];
      inmat[j][i]=inmat[i][j];         //symmetrize
    }
  }

  //Put corrmat entries into correct order (using 3*i mod 14) and coverting to covmat
  double** covmat = new double*[fNData];
  for(int i = 0; i < fNData; i++)
  {
    covmat[i] = new double[fNData];
    for(int j = 0; j < fNData; j++)
      covmat[i][j]=inmat[(3*i)%14][(3*j)%14]*totsys[i]*totsys[j];
  }

  // Now generate artificial systematics
  double** syscor = new double*[fNData];
  for(int i = 0; i < fNData; i++)
    syscor[i] = new double[fNData];

  if(!genArtSys(fNData,covmat,syscor))
   {
     cerr << " in " << fSetName << endl;
     exit(-1);
   }

  for (int i = 0; i < fNData; i++)
    for (int l = 0; l < fNData; l++)
    {
      fSys[i][l+1].add = syscor[i][l];
      fSys[i][l+1].mult = fSys[i][l+1].add*100/fData[i];
      fSys[i][l+1].type = ADD;
      fSys[i][l+1].name = "CORR";
    }
  f1.close();
  f2.close();
  f3.close();
  f4.close();

}

/**
 * LHCb 940pb^{-1}
 *
 * Z production > ee data from the LHCb experiment
 *
 * Final data from the LHCb paper: 1212.4620
 *
 * For the time being, only Z -> ee has been published with full experimental
 * correlation matrix provided with the measurement
 * Will follow the Z > mu mu analysis (at the moment is still preliminary) and
 * a W > l nu analysis, which is not yet at the conference note stage, so for the
 * time being we only use Z > ee and the old 36pb W > lnu data
 *
 * Luminosity uncertainty is about a constant 3.5% in
 * all data points and is not included in the systematic uncertainties
 *
 */

void LHCBZ940PBFilter::ReadData()
{
  cout << "**** LHCBWZ940PB - Only Z > ee filtered ****"<<endl;
  // Opening files
  fstream f1, f2;

  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/lhcb_940pb_zrap.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream datafile2("");
  datafile2 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_940pb_zrap.covmat";
  f2.open(datafile2.str().c_str(), ios::in);

  if (f2.fail()) {
    cerr << "Error opening data file " << datafile2.str() << endl;
    exit(-1);
  }


  // Initialize
  const int ndata_z = 9;
  const double convfac = 1000.; // Must multiply from pb to fb
  double MZ2 = pow(MZ,2.0);
  double s = 7000;

  double etamin,etamax;
  double sys_corr[fNData],fsr;
  double inmat[fNData][fNData];
  string line;

  for (int i = 0; i < ndata_z; i++)
    {
      getline(f1,line);
      istringstream lstream(line);

      lstream >> etamin >> etamax;
      fKin1[i] = (etamin+etamax) * 0.5;       // <eta>
      fKin2[i] = MZ2;
      fKin3[i] = s;

      lstream >> fData[i];
      fData[i] *= convfac;
      // stat uncertainty
      lstream >> fStat[i];
      fStat[i] *= convfac;

      // Uncorrelated systematics
      lstream >> fSys[i][1].add;
      fSys[i][1].add *= convfac;
      fSys[i][1].mult = fSys[i][1].add*100/fData[i];
      fSys[i][1].type = ADD;
      fSys[i][1].name = "UNCORR";

      // Sum in quandrature cor_sys and FSR
      lstream >> sys_corr[i] >> fsr;
      sys_corr[i] = convfac * sqrt(sys_corr[i]*sys_corr[i]+fsr*fsr);

      // Normalization uncertainty is defined both MULT (in %) and ADD (in abs value)
      fSys[i][0].mult = 3.5;                                // luminosity uncertainty 3.5%
      fSys[i][0].add = fSys[i][0].mult*fData[i]*1e-2;
      fSys[i][0].type = MULT;
      fSys[i][0].name = "CORR";
    }

  // Reading Covariance Matrix
  for (int i = 0; i < ndata_z; i++)
    for (int j = 0; j < i+1; j++)              // read only lower triangle
      f2 >> inmat[i][j];
  for (int i = 0; i < ndata_z; i++)
    for (int j = i+1; j<ndata_z; j++)
      inmat[i][j] = inmat[j][i];               // symmetrize


  //  Multiply by total systematic uncertainty
  double** covmat = new double*[fNData];
  for(int i = 0; i < fNData; i++)
  {
    covmat[i] = new double[fNData];
    for(int j = 0; j < fNData; j++)
      // Not sure whether is tot correlated  or total systematics
      // (in this case must add in quad. with uncorr!!!)
      covmat[i][j]=inmat[i][j]*sys_corr[i]*sys_corr[j];
  }

  // Now generate artificial systematics
  double** syscor = new double*[fNData];
  for(int i = 0; i < fNData; i++)
    syscor[i] = new double[fNData];

  if(!genArtSys(fNData,covmat,syscor))
   {
     cerr << " in " << fSetName << endl;
     exit(-1);
   }

  for (int i = 0; i < fNData; i++)
    for (int l = 0; l < fNData; l++)
    {
      fSys[i][l+2].add  = syscor[i][l];
      fSys[i][l+2].mult = fSys[i][l+2].add*100/fData[i];
      fSys[i][l+2].type = ADD;
      fSys[i][l+2].name = "CORR";
    }
  f1.close();
  f2.close();
}

/**
 * lhcb-lowmass
 *
 * This data is taken from LHCb-CONF-2012-013
 * THIS IS JUST A PROTOTYPE OF FILTER
 * IT'S NOT USING COMPLETE KIN INFO
 *
 */
void LHCBLOWMASS37PBFilter::ReadData()
{
  cout << "WARNING: kinematics are not implemented" << endl;

  // Opening files
  fstream f1;

  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/LHCb-37pb-lowmassdy.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  // Reading data
  string tmp;
  getline(f1,tmp);

  for (int i = 0; i < fNData; i++)
    {
      double mbin[2];

      // Read
      f1 >> mbin[0] >> mbin[1] >> fData[i] >> fStat[i] >> fSys[i][0].add >> fSys[i][1].add >> tmp;

      // Load
      fKin2[i] = pow(0.5*(mbin[0] + mbin[1]),2.0);
      fKin3[i] = 7E3;

      fSys[i][0].mult = fSys[i][0].add*100/fData[i];
      fSys[i][0].type = ADD;
      fSys[i][0].name = "UNCORR";

      fSys[i][1].mult = fSys[i][1].add*100/fData[i];
      fSys[i][1].type = MULT;
      fSys[i][1].name = "CORR";
    }

  f1.close();
}

/********************* NEW DATA in NNPDF3.1 **************************
*
* LHCb 1fb^{-1}
*
* W production > mu nu_mu data from the LHCb experiment
*
* Final data from the LHCb preprint: 1408.4354
* Luminosity uncertainty is a 1.71% in
* all data points and is quoted separately from other sources
* of systematic uncertainty
*/

void LHCBWMU1FBFilter::ReadData()
{
  // Opening files
  fstream f1, f2, f3;

  stringstream datafile("");
  datafile << dataPath() << "rawdata/"
  << fSetName << "/lhcb_wplrap.data";
  f1.open(datafile.str().c_str(), ios::in);

  if (f1.fail()) {
    cerr << "Error opening data file " << datafile.str() << endl;
    exit(-1);
  }

  stringstream datafile2("");
  datafile2 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_wmlrap.data";
  f2.open(datafile2.str().c_str(), ios::in);

  if (f2.fail()) {
    cerr << "Error opening data file " << datafile2.str() << endl;
    exit(-1);
  }

  stringstream datafile3("");
  datafile3 << dataPath() << "rawdata/"
   << fSetName << "/lhcb_covmat.data";
  f3.open(datafile3.str().c_str(), ios::in);

  if (f3.fail()) {
    cerr << "Error opening data file " << datafile3.str() << endl;
    exit(-1);
  }

  // Starting filter
  const int ndata_wp = 8;
  const int ndata_wm = 8;
  double binsize;  // Must multiply by binsize to match inclusive bin-by-bin data
  const double convfac = 1000.; // Must multiply from pb to fb
  double MW2 = pow(MW,2.0);
  double s = 7000;
  string line;

  double totsys[fNData];
  double etamin, etamax;
  int idat = 0;

  cout << "********** WARNING: Converting pb to fb to match ApplGrid output ********" << endl;

  // W+
  for (int i = 0; i < ndata_wp; i++)
  {
    getline(f1,line);
    istringstream lstream(line);

    lstream >> etamin >> etamax;
    binsize=1./(etamax-etamin);
    fKin1[idat+i] = (etamax + etamin)*0.5;     //eta
    fKin2[idat+i] = MW2;                       //mass W squared
    fKin3[idat+i] = s;                         //sqrt(s)

    lstream >> fData[idat+i];
    fData[idat+i] *= convfac;
    fData[idat+i] *= binsize;
    lstream >> fStat[idat+i];
    fStat[idat+i] *= convfac;
    fStat[idat+i] *= binsize;
    lstream >> totsys[idat+i];
    totsys[idat+i] *= convfac;
    totsys[idat+i] *= binsize;

    fSys[idat+i][0].mult = 1.71;                     //luminosity uncertainty of 1.71%
    fSys[idat+i][0].add = fSys[idat+i][0].mult*fData[i]*1e-2;
    fSys[idat+i][0].type = MULT;
    fSys[idat+i][0].name = "CORR";
  }
  idat+=ndata_wp;

  // W-
  for (int i = 0; i < ndata_wm; i++)
  {
    getline(f2,line);
    istringstream lstream(line);

    lstream >> etamin >> etamax;
    binsize=1./(etamax-etamin);
    fKin1[idat+i] = (etamax + etamin)*0.5;     //eta
    fKin2[idat+i] = MW2;                       //mass W squared
    fKin3[idat+i] = s;                         //sqrt(s)

    lstream >> fData[idat+i];
    fData[idat+i] *= convfac;
    fData[idat+i] *= binsize;
    lstream >> fStat[idat+i];
    fStat[idat+i] *= convfac;
    fStat[idat+i] *= binsize;
    lstream >> totsys[idat+i];
    totsys[idat+i] *= convfac;
    totsys[idat+i] *= binsize;

    fSys[idat+i][0].mult = 1.71;                     //luminosity uncertainty of 1.71%
    fSys[idat+i][0].add = fSys[idat+i][0].mult*fData[i]*1e-2;
    fSys[idat+i][0].type = MULT;
    fSys[idat+i][0].name = "CORR";
  }
  idat+=ndata_wm;

  //Reading correlation matrix
  //Format of table means we need to read all 15 points (W+,W- and Z)
  double inmat[16][16];
  for (int i = 0; i < 16; i++)
  {
    getline(f3,line);
    istringstream lstream(line);
    for (int j = 0; j < i+1; j++)      //Only lower diagonal in file
    {
      lstream >> inmat[i][j];
      inmat[j][i]=inmat[i][j];         //symmetrize
    }
  }

  //Put corrmat entries into correct order
  double** covmat = new double*[fNData];
  for(int i = 0; i < fNData-1; i++)
  {
    covmat[i] = new double[fNData];
    for(int j = 0; j < fNData-1; j++)
      covmat[i][j]=inmat[(2*i)%15][(2*j)%15]*totsys[i]*totsys[j];
    covmat[i][15]=inmat[(2*i)%15][15]*totsys[i]*totsys[15];
  }
  covmat[15] = new double[fNData];
  for(int j = 0; j < fNData-1;j++)
  	covmat[15][j]=inmat[15][(2*j)%15]*totsys[15]*totsys[j];
  covmat[15][15]=inmat[15][15]*totsys[15]*totsys[15];

  // Now generate artificial systematics
  double** syscor = new double*[fNData];
  for(int i = 0; i < fNData; i++)
    syscor[i] = new double[fNData];

  if(!genArtSys(fNData,covmat,syscor))
   {
     cerr << " in " << fSetName << endl;
     exit(-1);
   }

  for (int i = 0; i < fNData; i++)
    for (int l = 0; l < fNData; l++)
    {
      fSys[i][l+1].add = syscor[i][l];
      fSys[i][l+1].mult = fSys[i][l+1].add*100/fData[i];
      fSys[i][l+1].type = ADD;
      fSys[i][l+1].name = "CORR";
    }
  f1.close();
  f2.close();
  f3.close();
}


/****************
 * LHCb 2fb^{-1}
 *
 * Z production > e+e- data from the LHCb experiment
 *                8 TeV data
 * Final data from the LHCb preprint: 1503.00963
 * Luminosity uncertainty is a 1.2% in all data points and is quoted separately 
 * from other sources of systematic uncertainty
 */

void LHCBZEE2FBFilter::ReadData()
{
  // Opening files
  fstream f1, f2;
  
  stringstream datafile1("");
  datafile1 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_zrap.data";
  f1.open(datafile1.str().c_str(), ios::in);
  
  if (f1.fail()) {
    cerr << "Error opening data file " << datafile1.str() << endl;
    exit(-1);
  }

  stringstream datafile2("");
  datafile2 << dataPath() << "rawdata/"
  << fSetName << "/lhcb_zrap.corr";
  f2.open(datafile2.str().c_str(), ios::in);
  
  if (f2.fail()) {
    cerr << "Error opening data file " << datafile2.str() << endl;
    exit(-1);
  }

 
  // Initialize
  const int ndata_z = 17;
  const double convfac = 1000.; // Must multiply from pb to fb
  double MZ2 = pow(MZ,2.0);
  double s = 8000.;
  
  double etamin,etamax;
  double sys_corr[fNData],lumi[fNData],tot_unc[fNData];
  double inmat[fNData][fNData];
  string line;

  for (int i = 0; i < ndata_z; i++)
    {
      getline(f1,line);
      istringstream lstream(line);   
      
      lstream >> etamin >> etamax;
      fKin1[i] = (etamin+etamax) * 0.5;       // <eta>
      fKin2[i] = MZ2;
      fKin3[i] = s;

      lstream >> fData[i];
      fData[i] *= convfac;
      // stat uncertainty
      lstream >> fStat[i];
      fStat[i] *= convfac;
      
      // Uncorrelated systematics
      lstream >> fSys[i][0].add;
      fSys[i][0].add *= convfac;
      fSys[i][0].mult = fSys[i][0].add*100/fData[i];
      fSys[i][0].type = ADD;
      fSys[i][0].name = "UNCORR";
      
      // Correlated and luminosity uncertainties
      lstream >> sys_corr[i] >> lumi[i];
      sys_corr[i] *= convfac; 
      lumi[i] *= convfac;

      // Total uncertainty
      tot_unc[i] = pow(sys_corr[i]*sys_corr[i]+fSys[i][0].add*fSys[i][0].add+fStat[i]*fStat[i],0.5);
      
      // Normalization uncertainty is defined both MULT (in %) and ADD (in abs value)
      fSys[i][1].mult = lumi[i];
      fSys[i][1].add = fSys[i][1].mult*fData[i]*1e-2;
      fSys[i][1].type = MULT;
      fSys[i][1].name = "CORR";
    }

  // Reading Covariance Matrix
  for (int i = 0; i < ndata_z; i++)
    for (int j = 0; j < i+1; j++)              // read only lower triangle
      f2 >> inmat[i][j];
  for (int i = 0; i < ndata_z; i++)
    for (int j = i+1; j<ndata_z; j++)
      inmat[i][j] = inmat[j][i];               // symmetrize
  
  //  Multiply by total systematic uncertainty
  double** covmat = new double*[fNData];
  for(int i = 0; i < fNData; i++)
  {
    covmat[i] = new double[fNData];
    for(int j = 0; j < fNData; j++)
      // Not sure whether is tot correlated  or total systematics 
      //      covmat[i][j]=inmat[i][j]*sys_corr[i]*sys_corr[j]; 
      covmat[i][j]=inmat[i][j]*tot_unc[i]*tot_unc[j]; 
  }

  // Now generate artificial systematics
  double** syscor = new double*[fNData];
  for(int i = 0; i < fNData; i++)
    syscor[i] = new double[fNData];
    
  if(!genArtSys(fNData,covmat,syscor))
   {
     cerr << " in " << fSetName << endl;
     exit(-1);
   }

  for (int i = 0; i < fNData; i++)
    for (int l = 2; l < fNData; l++)
    {
      fSys[i][l].add  = syscor[i][l];
      fSys[i][l].mult = fSys[i][l].add*100/fData[i];
      fSys[i][l].type = ADD;
      fSys[i][l].name = "CORR";
    }
  f1.close();
  f2.close();
}
