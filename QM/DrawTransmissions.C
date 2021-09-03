
#include "TString.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TF1.h"
#include "TLine.h"
#include "TLegend.h"


#include <iostream>

using namespace std;

void DrawTransmissions()
{

  
  // TLegend *leg = new TLegend(0.7, 0.6, 0.88, 0.88);



  double x1 = 0;
  double x2 = 10;
  double mass = 100.;
  double V0 = x2/3.;
  //  TH2D tmp("tmp", "tmp", 100, x1, x2, 1000, -2, 15);

  // transmission coefficient as function of E
  // see Griffiths Problem 2.33, pg 83
  // setting a=m=1
  TF1 *SquareBarrierT = new TF1("Tbarrier", "(x < [0])*1./(1. + [0]^2/(4*x*([0]-x))*(sinh(2*sqrt(2*[1]*([0] - x))))^2)", x1, x2);
  SquareBarrierT -> SetLineColor(kRed);
  SquareBarrierT -> SetParameter(0, V0); // set barrier height
  SquareBarrierT -> SetParameter(1, mass);
  SquareBarrierT -> SetNpx(20000);



  TF1 *SquareWellT = new TF1("Twell", "1./(1. + [0]^2/(4*x*([0]+x))*(sin(2*sqrt(2*[1]*([0] + x))))^2)", x1, x2);
  SquareWellT -> SetLineColor(kBlue);
  SquareWellT -> SetParameter(0, V0); // set the potential depth
  SquareWellT -> SetParameter(1, mass);
  SquareWellT -> SetNpx(2000);


  SquareWellT -> Draw();
  SquareBarrierT -> Draw("same");

  TF1 *constfun = new TF1(Form("C%i", 1), "[0]", x1, x2);
  constfun -> SetParameter(0, 1.);
  constfun -> SetLineColor(1);
  constfun -> SetLineStyle(2);
  constfun -> Draw("same");

  TLine *line = new TLine(V0, 0., V0, 1.);
  line -> SetLineWidth(2);
  line -> Draw();


}
