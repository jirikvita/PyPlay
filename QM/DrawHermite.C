// JK 2014, 2016

#include "TString.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TF1.h"
#include "TLegend.h"
#include "TLine.h"


#include <iostream>

using namespace std;

void DrawHermite()
{

  const int Nfits = 6;
  TString Exp = "(exp(-x^2/2))";
  TString Forms[Nfits] = { "1",
			   "2*x",
			   "4*x^2-2",
			   "8*x^3-12*x", // "x*(8*x^2-12)",
			   "16*x^4-48*x^2+12", // "x^2*(16*x^2-48)+12",
			   "32*x^5-160*x^3+120*x" // "x*(x^2*(32*x^2-160)+120)" 
 };


  TLegend *leg[Nfits];
  TLegend *legRho[Nfits];
  for (int i = 0; i < Nfits; ++i) {
    leg[i] = 0;
    legRho[i] = 0;
  }

  double x2 = 5;
  double x1 = -x2;
  TH2D tmp("Harmonic oscilator wave functions", "Harmonic oscilator wave functions;#xi = #sqrt{#frac{m#omega}{#hbar}}x", 100, x1, x2, 1000, -2, 15);
  tmp.GetXaxis()->SetTitle("#xi");
  gStyle->SetOptTitle(0);
  
  TF1 *fun[Nfits];
  TF1 *funRho[Nfits];
  TF1 *constfun[Nfits];
  TLine *lines[Nfits]; // classical boundaries
  int cols[] = {kBlack, kRed, kRed+2, kBlue, kBlue+2, kGreen+2};
  tmp.SetStats(0);

  TString canname = "HarmOsc";
  TCanvas *can = new TCanvas(canname, canname, 0,0,1000,800);
  canname += "Rho";
  TCanvas *canRho = new TCanvas(canname, canname, 100,100,1000,800);
  can -> cd();
  tmp.GetYaxis()->SetTitle("#psi(#xi)");
  tmp.DrawCopy();
  canRho -> cd();
  tmp.GetYaxis()->SetTitle("#rho(#xi)");
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

    TString Norm = "1/sqrt(2^[0]*TMath::Factorial([0]))";
    TString HackShift = " + [1]";
    TString fullform = Norm + "*" + Exp + "*(" + Forms[i] + ")" + HackShift; // note the brackets!!!
    cout << fullform.Data() << endl;
    fun[i] = new TF1(Form("H_{%i}(#xi) exp(-#xi^{2}/2)", i), fullform, x1, x2);
    fun[i] -> SetParameter(0, i);
    fullform = "( " + Norm + "*" + Exp + "*(" + Forms[i] + ") )^2" + HackShift; // note the brackets!!!
    funRho[i] = new TF1(Form("H^{2}_{%i}(#xi) exp(-#xi^{2})", i), fullform, x1, x2);
    funRho[i] -> SetParameter(0, i);
    double shift = 2*i;
    double height = 1.;
    double xcl = sqrt(2*i+1.); // classical boundary

    fun[i] -> SetParameter(1, shift);
    fun[i] -> SetLineColor(cols[i]);
    can -> cd();
    fun[i] -> Draw(sameopt);
    constfun[i] = new TF1(Form("C%i", i), "[0]", x1, x2);
    constfun[i] -> SetParameter(0, fun[i] -> GetParameter(1));
    constfun[i] -> SetLineColor(1);
    constfun[i] -> SetLineStyle(2);
    constfun[i] -> Draw("same");
    lines[i] = new TLine(-xcl, shift-height, -xcl, shift+height);
    lines[i] -> SetLineColor(cols[i]);
    lines[i] -> Draw();
    TLine *copyline = (TLine*) lines[i] -> Clone();
    copyline -> SetX1(xcl);
    copyline -> SetX2(xcl);
    copyline -> Draw();
    leg[ileg] -> AddEntry(fun[i], TString(fun[i]->GetName()) + Form(" + %i", int(fun[i] -> GetParameter(1))), "L");
    legRho[ileg] -> AddEntry(funRho[i], TString(funRho[i]->GetName()) + Form(" + %i", int(fun[i] -> GetParameter(1))), "L");
    sameopt = "same";


    funRho[i] -> SetParameter(1, shift);
    funRho[i] -> SetLineColor(cols[i]);
    canRho -> cd();
    funRho[i] -> Draw(sameopt);
    constfun[i] -> Draw("same");
    lines[i] -> Draw();
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
