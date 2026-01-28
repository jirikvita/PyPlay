// JK 2014, 2016
// update 28.1.2026

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

  // STEERING!
  bool zeroShift = true;
  //bool zeroShift = false;
  gStyle->SetOptTitle(0);

  TLegend *leg[Nfits];
  TLegend *legRho[Nfits];
  for (int i = 0; i < Nfits; ++i) {
    leg[i] = 0;
    legRho[i] = 0;
  }

  double x2 = 5;
  double x1 = -x2;
  double y1 = -2;
  double y2 = 15;
  if (zeroShift) {
    y1 = -1;
    y2 = 2;
  }
  TH2D *tmp = new TH2D("Harmonic oscilator wave functions", "Harmonic oscilator wave functions;#xi = #sqrt{#frac{m#omega}{#hbar}}x", 100, x1, x2, 1000, y1, y2);
  tmp ->GetXaxis()->SetTitle("#xi");
  tmp ->SetStats(0);
  
  TF1 *fun[Nfits];
  TF1 *funRho[Nfits];
  TF1 *constfun[Nfits];
  TLine *lines[Nfits]; // classical boundaries
  TLine *linesRho[Nfits]; // classical boundaries
  int cols[] = {kBlack, kRed, kRed+2, kBlue, kBlue+2, kGreen+2};

  TString canname = "HarmOsc";
  TCanvas *can = new TCanvas(canname, canname, 0,0,1000,800);
  canname += "Rho";
  TCanvas *canRho = new TCanvas(canname, canname, 100,100,1000,800);
  can -> cd();
  tmp ->GetYaxis()->SetTitle("#psi(#xi)");
  tmp ->Draw();

  canRho -> cd();
  if (zeroShift) {
    y1 = -0.2;
    y2 = 1.75;
  }

  TH2D *tmpRho = new TH2D("Harmonic oscilator densities", "Harmonic oscilator densities;#xi = #sqrt{#frac{m#omega}{#hbar}}x", 100, x1, x2, 1000, y1, y2);
  tmpRho -> GetXaxis()->SetTitle("#xi");
  tmpRho ->SetStats(0);
  tmpRho -> GetYaxis()->SetTitle("#rho(#xi)");
  tmpRho -> Draw();
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
    fun[i] -> SetNpx(1000);
    fullform = "( " + Norm + "*" + Exp + "*(" + Forms[i] + ") )^2" + HackShift; // note the brackets!!!
    funRho[i] = new TF1(Form("H^{2}_{%i}(#xi) exp(-#xi^{2})", i), fullform, x1, x2);
    funRho[i] -> SetParameter(0, i);
    double shift = 0.;
    if (!zeroShift)
      shift = 2*i;
    double xcl = sqrt(2*i+1.); // classical boundary

    double alpha = 0.2;
    fun[i] -> SetParameter(1, shift);
    fun[i] -> SetLineColor(cols[i]);
    if (zeroShift) {
      fun[i] -> SetFillColorAlpha(cols[i], alpha);
      fun[i] -> SetFillStyle(1111);
    }
    can -> cd();
    fun[i] -> Draw(sameopt);
    constfun[i] = new TF1(Form("C%i", i), "[0]", x1, x2);
    constfun[i] -> SetParameter(0, fun[i] -> GetParameter(1));
    constfun[i] -> SetLineColor(1);
    constfun[i] -> SetLineStyle(2);
    constfun[i] -> Draw("same");
    double sf = 0.4;
    if (zeroShift)
      sf = 1.;
    lines[i] = new TLine(-xcl, shift-sf*tmp->GetYaxis()->GetXmin(), -xcl, shift+sf*tmp->GetYaxis()->GetXmin());
    lines[i] -> SetLineColor(cols[i]);
    lines[i] -> Draw();
    TLine *copyline = new TLine(xcl, shift-sf*tmp->GetYaxis()->GetXmin(), xcl, shift+sf*tmp->GetYaxis()->GetXmin());
    copyline -> SetLineColor(cols[i]);
    copyline -> Draw();
    TString legstr = TString(fun[i]->GetName());
    if (fun[i] -> GetParameter(1) > 0)
      legstr += Form(" + %i", int(fun[i] -> GetParameter(1)));
    leg[ileg] -> AddEntry(fun[i], legstr, "L");


    funRho[i] -> SetParameter(1, shift);
    funRho[i] -> SetLineColor(cols[i]);
    legstr = TString(funRho[i]->GetName());
    if (funRho[i] -> GetParameter(1) > 0)
      legstr += Form(" + %i", int(funRho[i] -> GetParameter(1)));
    legRho[ileg] -> AddEntry(funRho[i], legstr, "L");
    sameopt = "same";

    if (zeroShift) {
      funRho[i] -> SetFillColorAlpha(cols[i], alpha);
      funRho[i] -> SetFillStyle(1111);
    }
    funRho[i] -> SetNpx(1000);
    canRho -> cd();
    funRho[i] -> Draw(sameopt);
    constfun[i] -> Draw("same");
    double sf2 = sf;
    if (zeroShift)
      sf2 = 5;
    linesRho[i] = new TLine(-xcl, shift-sf2*tmpRho->GetYaxis()->GetXmin(),
			    -xcl, shift+sf*tmpRho->GetYaxis()->GetXmin());
    linesRho[i] -> SetLineColor(cols[i]);
    linesRho[i] -> Draw();
    TLine *copylineRho = new TLine(xcl, shift-sf2*tmpRho->GetYaxis()->GetXmin(),
				   xcl, shift+sf*tmpRho->GetYaxis()->GetXmin());
    copylineRho -> SetLineColor(cols[i]);
    copylineRho -> Draw();
       
  }

  can -> cd();
  for (int i = 0; i < Nfits; ++i) {
    if (leg[i]) {
      leg[i] -> Draw();
    }
  }

  TString tag = "";
  if (zeroShift)
    tag = "_noShift";
  TString pdfdir = "pdf/";
  TString pngdir = "png/";
  can -> Print(pngdir + TString(can -> GetName()) + tag + ".png");
  can -> Print(pdfdir + TString(can -> GetName()) + tag + ".pdf");

  canRho -> cd();
  for (int i = 0; i < Nfits; ++i) {
    if (leg[i]) {
      legRho[i] -> Draw();
    }
  }
  canRho -> Print(pngdir + TString(canRho -> GetName()) + tag + ".png");
  canRho -> Print(pdfdir + TString(canRho -> GetName()) + tag + ".pdf");
  
}
