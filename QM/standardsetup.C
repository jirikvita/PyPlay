#include <TStyle.h>

void setup()
{

 TStyle *plain  = new TStyle("Plain","Plain Style (no colors/fill areas)");
  
  plain->SetCanvasBorderMode(0);
  plain->SetPadBorderMode(0);
  plain->SetPadColor(0);
  plain->SetCanvasColor(0);
  plain->SetTitleColor(1);
  plain->SetStatColor(1);
  plain->SetOptFit(1111);
  plain->SetHistLineWidth(3);
  plain->SetHistLineStyle(0);

  plain->SetStatX(0.1);

  //plain->SetLabelOffset(1.2);
  //plain->SetLabelFont(1);
  //plain->SetLabelSize(5);

  gROOT->SetStyle("Plain");

  gStyle->SetOptFit(1100);

  //gStyle ->SetStatFontSize(0.03);
  gStyle ->SetStatW(0.26);//0.19
  gStyle ->SetStatH(0.18);//0.1
  gStyle->SetPadGridX(true);
  gStyle->SetPadGridY(true);
  gStyle->SetHistLineWidth(2);
  //gStyle->SetTitleH(0.11);
  //gStyle->SetTitleW(0.65);
gStyle->SetPalette(1);

//   gStyle->SetLabelSize();
  //gStyle ->SetTitleXSize(0.1);
  //gStyle ->SetTitleFontSize(0.05);
  

}
