// JK 2014, 2016, 17.10.2019

#include "TString.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TF1.h"
#include "TLegend.h"
#include "TLine.h"
#include "TStyle.h"


#include <iostream>

using namespace std;



void DrawInfWell1D()
{

  const int Nfits = 6;
  const double dshift = 4.5;
  

  TLine *lines[Nfits];
  TLegend *leg[Nfits];
  TLegend *legRho[Nfits];
  for (int i = 0; i < Nfits; ++i) {
    leg[i] = 0;
    legRho[i] = 0;
  }

  double x1 = 0.;
  double x2 = 1;

  TH2D tmp("Infinite square well wave functions", "Infinite square well wave functions", 100, x1, x2, 1000, -2, dshift*(Nfits+1)+3);
  tmp.GetXaxis()->SetTitle("x");
  gStyle->SetOptTitle(0);
  
  TF1 *fun[Nfits];
  TF1 *funRho[Nfits];
  TF1 *constfun[Nfits];
  int cols[] = {kBlack, kRed, kRed+2, kBlue, kBlue+2, kGreen+2};
  tmp.SetStats(0);

  TString canname = "InfWell1D";
  TCanvas *can = new TCanvas(canname, canname, 0,0,1000,800);
  canname += "Rho";
  TCanvas *canRho = new TCanvas(canname, canname, 100,100,1000,800);

  can -> cd();
  tmp.GetYaxis()->SetTitle("#psi(x)");
  tmp.DrawCopy();
  canRho -> cd();
  tmp.GetYaxis()->SetTitle("#rho(x)");
  tmp.DrawCopy();
  TString sameopt = "same";
  int ileg = 0;
  int Nleg = 3;
  for (int i = Nfits-1; i >= 0; --i) {
    // for (int i = 0; i < Nfits; ++i) {
    cout << "=== " << i << " ===" << endl;
    int j = Nfits-1 - i;
    ileg = j / Nleg;
    cout << "j=" << j << " ileg=" << ileg << endl;
    if (leg[ileg] == 0) {
      leg[ileg] = new TLegend(0.2+0.3*ileg, 0.75, 0.5+0.3*ileg, 0.88);
      leg[ileg] -> SetBorderSize(0);
      leg[ileg] -> SetFillColor(0);
    }
    if (legRho[ileg] == 0) {
      legRho[ileg] = new TLegend(0.2+0.3*ileg, 0.75, 0.5+0.3*ileg, 0.88);
      legRho[ileg] -> SetBorderSize(0);
      legRho[ileg] -> SetFillColor(0);
    }

    double shift = dshift*i;
    
    fun[i] = new TF1(Form("#sqrt{2/a} sin(%i #pi x / a)", i+1), "sqrt(2/[1])*sin([0]*TMath::Pi()*x / [1]) + [2]", x1, x2);
    fun[i] -> SetParameters(i+1, x2-x1, shift); 
    funRho[i] = new TF1(Form("2/a sin^{2}(%i #pi x / a)", i+1), "2/[1]*(sin([0]*TMath::Pi()*x / [1]))^2 + [2]", x1, x2);
    funRho[i] -> SetParameters(i+1, x2 - x1, shift);
    fun[i] -> SetLineColor(cols[i]);

    lines[i] = new TLine(x1, shift, x2, shift);
    lines[i] -> SetLineStyle(2);
    lines[i] -> SetLineColor(cols[i]);


    can -> cd();
    fun[i] -> Draw(sameopt);
    lines[i] -> Draw();
    
    leg[ileg] -> AddEntry(fun[i], TString(fun[i]->GetName()) + Form(" + %2.1f", shift), "L");
    legRho[ileg] -> AddEntry(funRho[i], TString(funRho[i]->GetName()) + Form(" + %2.1f", shift), "L");
    sameopt = "same";

    funRho[i] -> SetLineColor(cols[i]);
    canRho -> cd();
    funRho[i] -> Draw(sameopt);
    TLine *copyline = (TLine*) lines[i] -> Clone();
    copyline -> Draw();

    
  }

  can -> cd();
  for (int i = 0; i < Nfits; ++i) {
    if (leg[i]) {
      leg[i] -> Draw();
    }
  }
  can -> Print(TString(can -> GetName()) + ".png");
  can -> Print(TString(can -> GetName()) + ".pdf");

  canRho -> cd();
  for (int i = 0; i < Nfits; ++i) {
    if (leg[i]) {
      legRho[i] -> Draw();
    }
  }
  canRho -> Print(TString(canRho -> GetName()) + ".png");
  canRho -> Print(TString(canRho -> GetName()) + ".pdf");
  
}
