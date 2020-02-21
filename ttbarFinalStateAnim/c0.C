{
//=========Macro generated from canvas: c0/c0
//=========  (Tue Feb 17 12:44:56 2015) by ROOT version5.34/14
   TCanvas *c0 = new TCanvas("c0", "c0",605,219,790,777);
   c0->Range(0,0,1,1);
   c0->SetFillColor(0);
   c0->SetBorderMode(0);
   c0->SetBorderSize(2);
   c0->SetFrameBorderMode(0);
   TLine *line = new TLine(0.4743758,0.5150555,0.5190539,0.6656101);
   line->SetLineColor(2);
   line->SetLineWidth(3);
   line->Draw();
   line = new TLine(0.4717477,0.5103011,0.4296978,0.3645008);
   line->SetLineColor(4);
   line->SetLineWidth(3);
   line->Draw();
   TLatex *   tex = new TLatex(0.521682,0.5736926,"t");
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.4178712,0.429477,"#bar{t}");
   tex->SetLineWidth(2);
   tex->Draw();
   TMarker *marker = new TMarker(0.4743758,0.5094067,29);

   Int_t ci;   // for color index setting
   ci = TColor::GetColor("#ffcc00");
   marker->SetMarkerColor(ci);
   marker->SetMarkerStyle(29);
   marker->SetMarkerSize(3);
   marker->Draw();
   c0->Modified();
   c0->cd();
   c0->SetSelected(c0);
   c0->ToggleToolBar();

   c0->Print("c0.png");
   
}
