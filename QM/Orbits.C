// jiri kvita 2005, 2008, 2016
// qitek@matfyz.cz

#include "TCanvas.h"
#include "TAxis.h"
#include "TF2.h"
#include "TString.h"

#include <iostream>
using namespace std;

#include "standardsetup.C"


void Orbits()

{

  setup();

  // gStyle -> SetPalette(100);
  
  const int nmax = 10;
  const int lmax = nmax - 1;
  const int mmax = 2*lmax + 1;
  float maxx = 4.2, minx = -maxx, maxy = maxx, miny = -maxy;
  int npx = 120, npy = npx;
  int npxs = 70, npys = npxs;

  TString eqxyz[nmax][lmax][mmax];

  // TF1 x ... real cartesian x, y ... real cartesian z ;-)
  
  

  // 1s
  eqxyz[0][0][0] = "(2*sqrt(4/pi)*exp(-sqrt(x^2+y^2)))^2";
  
  // 2s
  eqxyz[1][0][0] = "(sqrt(4./pi)*(1. - 1./2.*sqrt(x^2+y^2))/(sqrt(2.))*exp(-sqrt(x^2+y^2)/2))^2";
  
  // something like 2pz
  eqxyz[1][1][1] = "(1/2.*sqrt(3/pi)*y/(2*sqrt(6))*exp(-sqrt(x^2+y^2)/2))^2";
  
  // 3dz^2
  eqxyz[2][2][2] = "(sqrt(5/(pi))/4*(3*(y/sqrt(x^2+y^2))^2-1)*(x^2+y^2)/sqrt(3)*exp(-sqrt(x^2+y^2))/2./3.)^2";

  // 4f l=3, m=0
  eqxyz[3][3][3] = "(sqrt(7/(pi))/4*(5*(y/sqrt(x^2+y^2))^3-3*y/sqrt(x^2+y^2))*sqrt(x^2+y^2)^3/(96*sqrt(35))*exp(-sqrt(x^2+y^2)/2./4.))^2";
  
  // 4f l=3, m=1
  eqxyz[3][3][4] = "(sqrt(21/(pi))/8*x/sqrt(x^2+y^2)*(5*(y/sqrt(x^2+y^2))^2-1)*sqrt(x^2+y^2)^3/(96*sqrt(35))*exp(-sqrt(x^2+y^2)/2./4.))^2";

  // 4f l=3, m=2
  eqxyz[3][3][5] = "(sqrt(105/(2*pi))/4*y*x^2/(sqrt(x^2+y^2))^3*sqrt(x^2+y^2)^3/(96*sqrt(35))*exp(-sqrt(x^2+y^2)/2/4))^2";

  // 4f l=3, m=3
  eqxyz[3][3][6] = "(sqrt(35/(pi))/8*(x/sqrt(x^2+y^2))^3*sqrt(x^2+y^2)^3/(96*sqrt(35))*exp(-sqrt(x^2+y^2)/2/4))^2";
  
  const int norb=8; 
 
  int n,l,m;
  TString name[norb] = {"1s", "2s", "3dz2",       "2pz",    "4fm0",    "4fm1",    "4fm2",    "4fm3"};
  TString text[norb] = {"1s", "2s", "3d_{z^{2}}", "2p_{z}", "4f, m=0", "4f, m=1", "4f, m=2", "4f, m=3"};
  TCanvas* c[norb];
  TF2 *orbital[norb];
 
  for(int i = 0; i < norb; ++i) {
   
    switch(i) {
    case 0: n=1; l=0; m=0; // 1s
      break;
    case 1: n=2; l=0; m=0;// 2s
      break;
    case 2: n=3; l=2; m=0;// 3dz2
      break;
    case 3: n=2; l=1; m=0;// 2pz
      break;
    case 4: n=4; l=3; m=0;// 4f l=3;  m=0
      break;
    case 5: n=4; l=3; m=1;// 4f l=3;  m=1
      break;
    case 6: n=4; l=3; m=2;// 4f l=3;  m=2
      break;
    case 7: n=4; l=3; m=3;// 4f l=3;  m=3
      break;
    }

    bool logz = false;
    if (i < 2) {
      maxx = 3.; //exp(2./n);
      minx = -maxx;
      maxy = maxx;
      miny = -maxy;
      if (n == 2)
	logz = true;
    } else if (i < 4) {
      maxx = 3.4*exp(2./n);
      minx = -maxx;
      maxy = maxx;
      miny = -maxy;
    } else {
      maxx = 6.4*n*exp(4./n);
      minx = -maxx;
      maxy = maxx;
      miny = -maxy;
    }
    
    cout << "Processing n=" << n
	 << " l=" << l
	 << " m=" << m
	 << " function: " << eqxyz[n-1][l][m+l].Data()
	 << endl;
	    
    orbital[i] = new TF2(eqxyz[n-1][l][m+l].Data(),
			 eqxyz[n-1][l][m+l].Data(),
			 minx, maxx, miny, maxy);
    orbital[i] -> SetNpx(npx);
    orbital[i] -> SetNpy(npy);
			     
    c[i] = new TCanvas(name[i], name[i], 10+i*80, 300-i*50, 900, 500);
    c[i] -> Divide(2,1);
    c[i] -> Draw();
    c[i] -> cd(1);

    if (logz)
      gPad -> SetLogz(logz);

    orbital[i] -> SetTitle(text[i]);
    TF2 *orb = (TF2*) orbital[i] -> DrawCopy("colz");
    TAxis *xa = orb -> GetXaxis();
    xa -> SetTitle("x / a");
    xa -> SetTitleOffset(1.15);
    
    TAxis *ya = orb -> GetYaxis();
    ya -> SetTitle("z / a");
    
    c[i] -> cd(2);
    gPad -> SetTheta(34.8234);
    gPad -> SetPhi(-66.8881);
    //    orbital[i] -> SetLineStyle(2);
    orbital[i] -> SetLineWidth(1);
    orbital[i] -> SetNpx(npxs);
    orbital[i] -> SetNpy(npys);
    
    orbital[i] -> Draw("surf1");
    xa = orbital[i] -> GetXaxis();
    xa -> SetTitle("x / a");
    ya = orbital[i] -> GetYaxis();
    ya -> SetTitle("z / a");

    c[i]->Print(TString(c[i]->GetName()) + ".pdf");
    c[i]->Print(TString(c[i]->GetName()) + ".png");

  }

}
